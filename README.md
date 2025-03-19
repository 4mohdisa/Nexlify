# Nexlify

Nexlify is a web application designed to convert web pages into Markdown files. It features a straightforward, light-themed interface where users can input URLs, tweak settings, and download the resulting Markdown files.

## Features

- Convert one or multiple URLs into Markdown files.
- Optional website crawling to gather additional pages.
- Adjustable settings for extraction (e.g., include links, specify data type).
- Download options for single or bulk Markdown files.

## Technology Stack

- **Frontend**: Built with HTML, CSS, and JavaScript, using ShadCN components.
- **Backend**: Powered by Python and FastAPI, with crawl4ai for crawling functionality.
- **Deployment**: Utilizes Docker for containerization.

## Setup

1. **Clone the repository**:

git clone https://github.com/yourusername/nexlify.git
   cd nexlify

2. **Frontend**:
- Go to the `frontend` folder.
- Serve the static files (e.g., run `python -m http.server`).

3. **Backend**:
- Enter the `backend` folder.
- Set up a virtual environment and install dependencies:
  ```
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```
- Launch the FastAPI server:
  ```
  uvicorn api.main:app --reload
  ```

4. **Access the application**:
- Visit `http://localhost:8000` in your browser for the frontend.
- The backend API runs at `http://localhost:8000`.

## Usage

1. **Input URL**: Type in the URL of the web page to convert.
2. **Adjust Settings**: Customize the process with toggles and dropdowns.
3. **Process**: Hit the "Process" button to begin conversion.
4. **Download**: Retrieve the Markdown file once conversion is done.

## License

Nexlify is released under the MIT License. Check the [LICENSE](LICENSE) file for details.