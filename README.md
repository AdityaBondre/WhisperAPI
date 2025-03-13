## High-Level Overview

The codebase is designed to provide a web-based service for transcribing audio files and summarizing their content, specifically targeting medical consultations. The service utilizes two main AI models: Whisper for transcription and Ollama for summarization. This service is built using the Flask framework for Python and is intended to be deployed using Gunicorn as a WSGI HTTP server.

## Architecture Codemap

### Key Components

1. **Flask Application (`app.py`)**:
   - **Purpose**: Serves as the entry point of the application. It handles HTTP requests, integrates AI models, processes files, and returns responses.
   - **Key Functions**:
     - `transcribe()`: Handles file uploads, uses the Whisper model to transcribe audio to text, and then summarizes the text using the Ollama model.
     - `home()`: Provides a simple health check route to confirm the API is running.
   - **Configuration**: Sets up CORS (Cross-Origin Resource Sharing) and defines the upload folder for storing incoming audio files temporarily.

2. **Whisper Model Integration**:
   - **Purpose**: Transcribes audio files to text.
   - **Integration Point**: Loaded at the start of the Flask app to ensure it's ready to transcribe any incoming audio files.

3. **Ollama Model Integration**:
   - **Purpose**: Summarizes the transcribed text focusing on critical medical information.
   - **Function**: `summarize_text()`, which takes transcribed text as input and returns a summarized version as output. It uses a predefined prompt to guide the AI for summarization.

4. **File Handling**:
   - **Operations**: Securely saving and deleting files.
   - **Security**: Uses `secure_filename` from Werkzeug to sanitize file names before saving them.

5. **Error Handling**:
   - **Scope**: Covers file upload issues, transcription failures, and summarization errors.
   - **Implementation**: Returns appropriate HTTP status codes and error messages based on the exception encountered.

### Deployment Script (`start.sh`)

- **Purpose**: Configures and starts the Gunicorn server with specified workers and binds it to a network address.
- **Usage**: This script is used to deploy the application in a production-like environment, ensuring it can handle multiple requests simultaneously by specifying multiple workers.

### Architectural Invariants

- **Model Dependency**: The Flask application is heavily dependent on the Whisper and Ollama models for its core functionality. These models must be available and correctly loaded for the application to function.
- **Statelessness**: The Flask application is stateless; it does not store any user data between requests. All necessary data is passed in client requests and does not persist beyond the lifecycle of the request.
- **File Handling Security**: No direct file paths are exposed to the end-user, and all file interactions are handled securely to prevent unauthorized access or directory traversal attacks.

### Boundaries and Interfaces

- **External Interfaces**:
  - The application exposes HTTP endpoints (`/transcribe` and `/`) for interaction with clients.
  - It accepts multipart/form-data for file uploads and returns JSON responses.
- **Internal Boundaries**:
  - Separation between web request handling (Flask routes) and AI model interactions (transcription and summarization).
  - File operations are encapsulated within the route handlers, ensuring that file logic is not spread across the application.

## Conclusion

This architecture provides a robust framework for a medical transcription and summarization service, leveraging advanced AI models and secure web practices. It is designed to be scalable and secure, with clear separation of concerns and well-defined interfaces for ease of maintenance and potential future enhancements.
