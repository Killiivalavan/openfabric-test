# Creative AI Pipeline

This application creates an end-to-end pipeline that transforms text prompts into 3D models through multiple AI services.

## Features

- Uses a local LLM (DeepSeek R1) to enhance text prompts
- Generates images from enhanced prompts using Openfabric's Text-to-Image service
- Converts images to 3D models using Openfabric's Image-to-3D service
- Maintains memory of past creations
- Supports referencing previous creations

## Setup & Requirements

### Prerequisites

1. [Ollama](https://ollama.com/) installed and running with the DeepSeek-r1 model
2. Docker for containerized deployment
3. Internet connection for Openfabric API access

### Installation

#### Running with Docker

1. Build the Docker image:
   ```
   docker build -t creative-ai-pipeline .
   ```

2. Run the container:
   ```
   docker run -p 8888:8888 creative-ai-pipeline
   ```

#### Running Locally

1. Install dependencies using Poetry:
   ```
   pip install poetry
   poetry install
   ```

2. Run the application:
   ```
   sh start.sh
   ```

### Ollama Setup

1. Install Ollama from [ollama.com](https://ollama.com/)
2. Pull the DeepSeek model:
   ```
   ollama pull deepseek-r1:latest
   ```
3. Start the Ollama service:
   ```
   ollama serve
   ```

## Usage

The application exposes a REST API endpoint that you can access via:
- Swagger UI: `http://localhost:8888/swagger-ui/#/App/post_execution`

### Example Requests

Basic prompt:
```json
{
  "prompt": "Make me a glowing dragon standing on a cliff at sunset"
}
```

Reference previous creations:
```json
{
  "prompt": "Create a robot like the dragon I made before, but with wings"
}
```

## Architecture

The application follows this pipeline flow:

1. User provides a text prompt
2. Local LLM (DeepSeek R1 via Ollama) enhances the prompt
3. Enhanced prompt is sent to Text-to-Image Openfabric service
4. Generated image is sent to Image-to-3D Openfabric service
5. Resulting 3D model is stored with memory of the creation
6. All generated assets are saved locally

## File Structure

- `main.py`: Main execution entry point
- `core/pipeline.py`: Orchestration of the entire pipeline
- `core/llm/`: LLM integration components
- `core/memory/`: Memory management
- `core/services/`: Service integrations for Openfabric
- `core/utils/`: Utility functions
- `datastore/`: Storage for memory and generated assets

## Memory System

The application uses:
- SQLite database for long-term memory
- In-memory storage for session memory
- Filesystem storage for generated assets

## Troubleshooting

- Ensure Ollama is running on http://localhost:11434
- Check logs for detailed error messages
- Verify internet connectivity for Openfabric API access

## License

Proprietary - All rights reserved 