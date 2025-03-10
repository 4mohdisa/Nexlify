# Nexlify Backend

This is the backend repository for Nexlify, a web application that converts web pages into Markdown files. The backend is responsible for handling API requests, crawling web pages, and generating Markdown content.

## File Structure

- `api/`: Contains the FastAPI application and route handlers.
- `crawler/`: Houses the web crawling logic.
- `markdown_generator/`: Manages the conversion of HTML to Markdown.
- `utils/`: Provides helper utilities like file handling and configuration.
- `models/`: Defines data models for requests and responses.
- `requirements.txt`: Lists all Python dependencies.
- `Dockerfile`: Provides instructions for containerizing the backend.

## Setup

1. **Clone the repository**:

    git clone https://github.com/yourusername/nexlify-backend.git
    cd nexlify-backend

2. **Create a virtual environment**:

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**:

    pip install -r requirements.txt

4. **Set up environment variables** (if necessary):

    - Create a `.env` file in the root directory.
    - Add any required variables, such as API keys or configuration settings.

## Running the Application

To start the backend server, run:

    uvicorn api.main:app --reload

The API will be available at `http://localhost:8000`. You can use tools like Postman or curl to test the endpoints.

## Testing the API

- **POST /crawl**: Send a JSON payload with the URL and settings to initiate crawling.
- **GET /download/{filename}**: Retrieve the generated Markdown file.

Example using curl:

    curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com", "settings": {"enable_crawling": true}}' http://localhost:8000/crawl