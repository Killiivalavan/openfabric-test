import json
import logging
import pprint
import traceback
from typing import Any, Dict, List, Literal, Tuple

import requests

from core.remote import Remote
from openfabric_pysdk.helper import has_resource_fields, json_schema_to_marshmallow, resolve_resources
from openfabric_pysdk.loader import OutputSchemaInst

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('openfabric_stub')

# Type aliases for clarity
Manifests = Dict[str, dict]
Schemas = Dict[str, Tuple[dict, dict]]
Connections = Dict[str, Remote]


class Stub:
    """
    Stub acts as a lightweight client interface that initializes remote connections
    to multiple Openfabric applications, fetching their manifests, schemas, and enabling
    execution of calls to these apps.

    Attributes:
        _schema (Schemas): Stores input/output schemas for each app ID.
        _manifest (Manifests): Stores manifest metadata for each app ID.
        _connections (Connections): Stores active Remote connections for each app ID.
    """

    # ----------------------------------------------------------------------
    def __init__(self, app_ids: List[str]):
        """
        Initializes the Stub instance by loading manifests, schemas, and connections
        for each given app ID.

        Args:
            app_ids (List[str]): A list of application identifiers (hostnames or URLs).
        """
        self._schema: Schemas = {}
        self._manifest: Manifests = {}
        self._connections: Connections = {}

        for app_id in app_ids:
            base_url = app_id.strip('/')

            # Add domain suffix if not present
            if '.node3.openfabric.network' not in base_url:
                base_url = f"{base_url}.node3.openfabric.network"
                
            logger.info(f"Initializing connection to app: {base_url}")

            try:
                # Fetch manifest with increased timeout
                manifest_url = f"https://{base_url}/manifest"
                logger.debug(f"Fetching manifest from: {manifest_url}")
                manifest_response = requests.get(manifest_url, timeout=15)
                
                if manifest_response.status_code != 200:
                    logger.error(f"Failed to fetch manifest. Status: {manifest_response.status_code}, Response: {manifest_response.text}")
                    continue
                    
                manifest = manifest_response.json()
                logger.info(f"[{app_id}] Manifest loaded successfully")
                logger.debug(f"Manifest content: {json.dumps(manifest, indent=2)}")
                self._manifest[app_id] = manifest

                # Fetch input schema with increased timeout
                schema_input_url = f"https://{base_url}/schema?type=input"
                logger.debug(f"Fetching input schema from: {schema_input_url}")
                input_schema_response = requests.get(schema_input_url, timeout=15)
                
                if input_schema_response.status_code != 200:
                    logger.error(f"Failed to fetch input schema. Status: {input_schema_response.status_code}, Response: {input_schema_response.text}")
                    continue
                    
                input_schema = input_schema_response.json()
                logger.info(f"[{app_id}] Input schema loaded successfully")
                logger.debug(f"Input schema content: {json.dumps(input_schema, indent=2)}")

                # Fetch output schema with increased timeout
                schema_output_url = f"https://{base_url}/schema?type=output"
                logger.debug(f"Fetching output schema from: {schema_output_url}")
                output_schema_response = requests.get(schema_output_url, timeout=15)
                
                if output_schema_response.status_code != 200:
                    logger.error(f"Failed to fetch output schema. Status: {output_schema_response.status_code}, Response: {output_schema_response.text}")
                    continue
                    
                output_schema = output_schema_response.json()
                logger.info(f"[{app_id}] Output schema loaded successfully")
                logger.debug(f"Output schema content: {json.dumps(output_schema, indent=2)}")
                self._schema[app_id] = (input_schema, output_schema)

                # Establish Remote WebSocket connection
                ws_url = f"wss://{base_url}/app"
                logger.debug(f"Establishing WebSocket connection to: {ws_url}")
                
                try:
                    self._connections[app_id] = Remote(ws_url, f"{app_id}-proxy").connect()
                    logger.info(f"[{app_id}] WebSocket connection established successfully")
                except Exception as ws_error:
                    logger.error(f"[{app_id}] WebSocket connection failed: {str(ws_error)}")
                    logger.debug(traceback.format_exc())
                    
            except requests.exceptions.ConnectionError as conn_error:
                logger.error(f"[{app_id}] Connection error: {str(conn_error)}")
                logger.debug(traceback.format_exc())
            except requests.exceptions.Timeout as timeout_error:
                logger.error(f"[{app_id}] Request timed out: {str(timeout_error)}")
                logger.debug(traceback.format_exc())
            except json.JSONDecodeError as json_error:
                logger.error(f"[{app_id}] JSON parsing error: {str(json_error)}")
                logger.debug(traceback.format_exc())
            except Exception as e:
                logger.error(f"[{app_id}] Initialization failed: {str(e)}")
                logger.debug(traceback.format_exc())

    # ----------------------------------------------------------------------
    def call(self, app_id: str, data: Any, uid: str = 'super-user') -> dict:
        """
        Sends a request to the specified app via its Remote connection.

        Args:
            app_id (str): The application ID to route the request to.
            data (Any): The input data to send to the app.
            uid (str): The unique user/session identifier for tracking (default: 'super-user').

        Returns:
            dict: The output data returned by the app.

        Raises:
            Exception: If no connection is found for the provided app ID, or execution fails.
        """
        connection = self._connections.get(app_id)
        if not connection:
            error_msg = f"Connection not found for app ID: {app_id}"
            logger.error(error_msg)
            raise Exception(error_msg)

        try:
            logger.info(f"[{app_id}] Sending request with data: {json.dumps(data) if isinstance(data, dict) else 'binary data'}")
            
            handler = connection.execute(data, uid)
            logger.debug(f"[{app_id}] Request sent, received handler: {handler}")
            
            result = connection.get_response(handler)
            logger.info(f"[{app_id}] Received response")
            
            if isinstance(result, dict):
                logger.debug(f"[{app_id}] Response keys: {list(result.keys())}")
            else:
                logger.debug(f"[{app_id}] Response type: {type(result)}")

            schema = self.schema(app_id, 'output')
            marshmallow = json_schema_to_marshmallow(schema)
            handle_resources = has_resource_fields(marshmallow())

            if handle_resources:
                logger.debug(f"[{app_id}] Resolving resources in response")
                result = resolve_resources("https://" + app_id + "/resource?reid={reid}", result, marshmallow())

            return result
        except Exception as e:
            logger.error(f"[{app_id}] Execution failed: {str(e)}")
            logger.debug(traceback.format_exc())
            raise

    # ----------------------------------------------------------------------
    def manifest(self, app_id: str) -> dict:
        """
        Retrieves the manifest metadata for a specific application.

        Args:
            app_id (str): The application ID for which to retrieve the manifest.

        Returns:
            dict: The manifest data for the app, or an empty dictionary if not found.
        """
        return self._manifest.get(app_id, {})

    # ----------------------------------------------------------------------
    def schema(self, app_id: str, type: Literal['input', 'output']) -> dict:
        """
        Retrieves the input or output schema for a specific application.

        Args:
            app_id (str): The application ID for which to retrieve the schema.
            type (Literal['input', 'output']): The type of schema to retrieve.

        Returns:
            dict: The requested schema (input or output).

        Raises:
            ValueError: If the schema type is invalid or the schema is not found.
        """
        _input, _output = self._schema.get(app_id, (None, None))

        if type == 'input':
            if _input is None:
                raise ValueError(f"Input schema not found for app ID: {app_id}")
            return _input
        elif type == 'output':
            if _output is None:
                raise ValueError(f"Output schema not found for app ID: {app_id}")
            return _output
        else:
            raise ValueError("Type must be either 'input' or 'output'")
