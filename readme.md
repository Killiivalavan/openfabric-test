# 🌟 AI Creative Generation Pipeline

A sophisticated AI application that transforms simple text prompts into stunning images and 3D models using a combination of local LLMs and Openfabric AI services.

## 🚀 Project Overview

This project implements an end-to-end creative pipeline that:

1. Takes a text prompt from the user
2. Enhances the prompt using a local LLM (DeepSeek or Llama)
3. Generates an image from the enhanced prompt using Openfabric Text-to-Image service
4. Transforms that image into a 3D model using Openfabric Image-to-3D service
5. Stores the creations in memory for future reference

The application features both short-term memory (session-based) and long-term memory (persistent database storage), allowing for references to previous creations.

## 🧠 Technical Architecture

### File Structure

```
├── app/                           # Main application directory
│   ├── core/                      # Core application components
│   │   ├── llm/                   # LLM integration
│   │   │   └── ollama_client.py   # Client for Ollama LLM services
│   │   ├── memory/                # Memory storage implementation
│   │   │   └── memory_manager.py  # Manages short and long-term memory
│   │   ├── services/              # API service integrations
│   │   │   ├── text_to_image.py   # Text-to-Image Openfabric service
│   │   │   ├── image_to_3d.py     # Image-to-3D Openfabric service
│   │   │   ├── mock_text_to_image.py  # Mock implementation for offline testing
│   │   │   └── mock_image_to_3d.py    # Mock implementation for offline testing
│   │   ├── utils/                 # Utility functions
│   │   ├── stub.py                # Openfabric SDK Stub implementation
│   │   ├── remote.py              # Remote service connection handling
│   │   ├── pipeline.py            # Main creative pipeline implementation
│   │   └── mock_pipeline.py       # Mock pipeline for offline testing
│   ├── config/                    # Configuration files
│   │   ├── state.json             # Application state configuration
│   │   ├── manifest.json          # App manifest defining capabilities
│   │   ├── execution.json         # Execution configuration
│   │   └── properties.json        # Properties configuration
│   ├── datastore/                 # Data storage directory
│   │   └── memory.db              # SQLite database for long-term memory
│   ├── main.py                    # Application entry point
│   ├── ignite.py                  # Startup script
│   ├── Dockerfile                 # Docker configuration
│   ├── start.sh                   # Startup script for local execution
│   └── pyproject.toml             # Project dependencies (Poetry)
├── datastore/                     # Root-level datastore directory
├── onto/                          # Ontology-related files
└── test_*.py                      # Various test files
```

### Core Components

#### 1. Pipeline Architecture (`app/core/pipeline.py`)

The `CreativePipeline` class orchestrates the entire workflow:

- Initializes all necessary components (LLM, memory, services)
- Processes user prompts through the entire pipeline
- Handles error states and partial successes
- Stores results in memory

The pipeline follows these steps:
1. Retrieves memory context if a reference query is provided
2. Enhances the prompt with the LLM
3. Generates an image from the enhanced prompt
4. Creates a 3D model from the image
5. Stores everything in memory

A `MockCreativePipeline` is available for offline testing without Openfabric services.

#### 2. Memory Management (`app/core/memory/memory_manager.py`)

The `MemoryManager` implements a sophisticated dual-layer memory system:

- **Short-term memory**: In-memory storage for the current session
- **Long-term memory**: SQLite database for persistent storage

Key features:
- Stores creations with metadata, tags, file paths
- Supports retrieval by ID, keyword search, and semantic similarity
- Generates memory context for LLM reference
- Tracks timestamps for chronological ordering

#### 3. LLM Integration (`app/core/llm/ollama_client.py`)

The `OllamaClient` connects to a local Ollama instance running models like DeepSeek or Llama:

- Enhances creative prompts with artistic details
- Extracts style tags and mood information
- Handles connection timeouts and retries
- Supports context-aware prompt enhancement using past creations

#### 4. Openfabric Service Integration

Two primary services are integrated through the Openfabric SDK:

- **TextToImageService** (`app/core/services/text_to_image.py`):
  - Connects to Openfabric's Text-to-Image service
  - Processes enhanced prompts into images
  - Handles response parsing and image storage
  
- **ImageTo3DService** (`app/core/services/image_to_3d.py`):
  - Connects to Openfabric's Image-to-3D service
  - Transforms 2D images into 3D models
  - Manages model file output and metadata

#### 5. SDK Integration (`app/core/stub.py` and `app/core/remote.py`)

- `Stub` class handles communication with Openfabric's API
- `Remote` class manages connection parameters and authentication
- Together they enable dynamic schema fetching and service calls

### Application Entry Point (`app/main.py`)

The main execution flow:

1. Receives user input through the Openfabric SDK
2. Extracts reference queries if present (for memory lookups)
3. Tests connection to Openfabric services
4. Uses real services if available, falls back to mock implementations if not
5. Processes the prompt through the pipeline
6. Returns detailed response with paths to generated files

## 💾 Data Persistence

The application uses SQLite for persistent storage in `datastore/memory.db`. The database schema includes:

- **creations table**: Stores all generated content
  - id: Unique identifier
  - timestamp: Creation time
  - user_prompt: Original user input
  - enhanced_prompt: LLM-enhanced prompt
  - image_path: Path to generated image
  - model_path: Path to generated 3D model
  - metadata: JSON-formatted additional information
  - tags: JSON-formatted search tags

## 🚪 Entry Points

- **API Access**: The application runs on port 8888 and provides a Swagger UI at `http://localhost:8888/swagger-ui/#/App/post_execution`
- **Docker**: Build and run using the provided Dockerfile
- **Local Execution**: Run the application locally using `start.sh`

## 🧩 Service Integration

### Openfabric AI Services

The application integrates with two key Openfabric services:

1. **Text to Image** (App ID: `f0997a01-d6d3-a5fe-53d8-561300318557`)
   - Converts text descriptions into high-quality images
   - Dynamically fetches service schema for request structuring
   - Handles API authentication and response processing

2. **Image to 3D** (App ID: `69543f29-4d41-4afc-7f29-3d51591f11eb`)
   - Transforms 2D images into 3D models
   - Supports various model output formats
   - Manages file transfer and conversion

### Local LLM Integration

The application communicates with a locally-running Ollama instance:

- Default model: `deepseek-r1:latest`
- Connection handling for both Docker and local environments
- Fallback mechanisms for offline operation

## 🛠️ Technical Details

### Prompt Enhancement

The LLM enhances user prompts by:
- Adding artistic details
- Specifying lighting and composition
- Suggesting style elements
- Extracting tags and mood indicators

Example transformation:
```
User prompt: "Make a dragon"
Enhanced: "Create a majestic fire-breathing dragon with iridescent scales, standing on a rocky cliff against a dramatic sunset sky with orange and purple hues. The dragon has amber eyes that glow with inner fire, massive leathery wings spread wide, and smoke curling from its nostrils."
```

### Mock Implementation

For offline development and testing, the application includes mock implementations:

- `MockCreativePipeline`: Simulates the full pipeline
- `MockTextToImageService`: Returns sample images
- `MockImageTo3DService`: Provides sample 3D models

These mocks enable development without requiring Openfabric service access.

### Resource Handling

The `ResourceHandler` utility manages:
- File paths and directories
- Temporary file storage
- Unique ID generation
- Binary data conversion

### Error Handling

The application implements robust error handling:
- Service connection failures
- LLM timeouts
- File I/O errors
- Database exceptions

Failed operations degrade gracefully, returning partial results when possible.

## 📋 Requirements

- Python 3.8+
- Ollama running locally (for LLM functionality)
- Docker (optional, for containerized execution)
- Openfabric SDK and account (for production use)

## 🚀 Getting Started

1. Ensure Ollama is running locally with the DeepSeek model:
   ```
   ollama run deepseek-r1:latest
   ```

2. Run the application:
   ```
   ./start.sh
   ```
   
   Or using Docker:
   ```
   docker build -t ai-creative-pipeline .
   docker run -p 8888:8888 ai-creative-pipeline
   ```

3. Access the API at http://localhost:8888/swagger-ui/

4. Send a request with a creative prompt:
   ```json
   {
     "prompt": "Create a glowing dragon standing on a cliff at sunset"
   }
   ```

## 📝 Testing

The project includes multiple test files:
- `test_app.py`: End-to-end application tests
- `test_memory.py`: Memory system tests
- `test_ollama.py`: LLM integration tests
- `test_components.py`: Individual component tests
- `test_pipeline.py`: Pipeline flow tests
- `test_full_pipeline.py`: Complete workflow tests

Run tests using:
```
python -m pytest
```

## 🌐 Future Enhancements

- FAISS/ChromaDB integration for vector-based memory search
- Web UI with Streamlit or Gradio
- Voice-to-text input capabilities
- Local 3D model browser
- Animation capabilities for 3D models