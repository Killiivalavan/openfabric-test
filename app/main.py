import logging
import re
from typing import Dict, Optional

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub
from core.pipeline import CreativePipeline
from core.mock_pipeline import MockCreativePipeline

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

############################################################
# Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
# Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """

    # Retrieve input
    request: InputClass = model.request
    user_prompt = request.prompt
    
    if not user_prompt:
        model.response.message = "Error: No prompt provided"
        return

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"Configurations: {configurations}")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else []
    
    # Ensure we have the required app IDs
    if 'f0997a01-d6d3-a5fe-53d8-561300318557' not in app_ids:
        app_ids.append('f0997a01-d6d3-a5fe-53d8-561300318557')  # Text-to-Image app
    if '69543f29-4d41-4afc-7f29-3d51591f11eb' not in app_ids:
        app_ids.append('69543f29-4d41-4afc-7f29-3d51591f11eb')  # Image-to-3D app
    
    stub = Stub(app_ids)
    
    # Extract reference query if present
    reference_query = extract_reference_query(user_prompt)
    
    # Try to test connection to Openfabric services
    use_mock = True
    try:
        logging.info("Testing connection to Openfabric services...")
        # Create a test pipeline to check if services are available
        test_pipeline = CreativePipeline(stub)
        # Try to get schema which will test the connection
        text_to_image_schema = test_pipeline.text_to_image.get_schema()
        if text_to_image_schema:
            logging.info("Successfully connected to Openfabric services")
            use_mock = False
    except Exception as e:
        logging.warning(f"Failed to connect to Openfabric services: {str(e)}")
        logging.info("Will use mock implementations instead")
    
    # Initialize and run the appropriate pipeline
    if use_mock:
        logging.warning("Using MOCK pipeline - Openfabric services unavailable")
        pipeline = MockCreativePipeline(stub)
    else:
        logging.info("Using real pipeline with Openfabric services")
        pipeline = CreativePipeline(stub)
    
    result = pipeline.process(user_prompt, reference_query)
    
    # Prepare response
    response: OutputClass = model.response
    
    # Add mock warning message if using mocks
    mock_warning = ""
    if use_mock or (result.get("mock", False)):
        mock_warning = "⚠️ NOTE: This response was generated using MOCK services because Openfabric services are unavailable.\n\n"
    
    if result["success"]:
        if result["model_path"]:
            response.message = f"{mock_warning}Successfully created both image and 3D model!\n\n" \
                               f"Original prompt: '{user_prompt}'\n" \
                               f"Enhanced prompt: '{result['enhanced_prompt']}'\n\n" \
                               f"Image saved at: {result['image_path']}\n" \
                               f"3D model saved at: {result['model_path']}"
        else:
            response.message = f"{mock_warning}Successfully created image but 3D model generation failed.\n\n" \
                               f"Original prompt: '{user_prompt}'\n" \
                               f"Enhanced prompt: '{result['enhanced_prompt']}'\n\n" \
                               f"Image saved at: {result['image_path']}\n" \
                               f"Error with 3D model: {result['error']}"
    else:
        response.message = f"{mock_warning}Error: {result['error']}\n" \
                           f"Original prompt: '{user_prompt}'"


def extract_reference_query(prompt: str) -> Optional[str]:
    """
    Extract a reference query from a prompt if it contains specific patterns 
    like "like the one I created before" or similar phrases.
    
    Args:
        prompt: The user prompt to analyze
        
    Returns:
        Optional query string for memory lookup, or None if no reference found
    """
    # Pattern for "like the X I created/made before/earlier/last time"
    like_pattern = r'like the (.*?) I (created|made) (before|earlier|last time|previously)'
    like_match = re.search(like_pattern, prompt, re.IGNORECASE)
    
    if like_match:
        return like_match.group(1)
    
    # Pattern for "similar to my X"
    similar_pattern = r'similar to (my|the) (.*?)(\.|\s|$)'
    similar_match = re.search(similar_pattern, prompt, re.IGNORECASE)
    
    if similar_match:
        return similar_match.group(2)
        
    return None