# File and Image Compression Website

A simple web application to compress images (JPEG, PNG) and documents (PDF, DOCX) using a Python Flask backend and a modern HTML/CSS/JS frontend.

## Features
- Support for JPEG, PNG, PDF, and DOCX formats.
- Adjustable compression quality for images.
- Real-time compression progress and results.
- No fixed file size limits.
- Responsive design.

## Project Structure
- `backend/`: Python Flask server and compression logic.
- `frontend/`: HTML, CSS, and JavaScript files for the user interface.

## Prerequisites
- Python 3.8+
- pip (Python package manager)

## Setup Instructions

### 1. Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask server:
   ```bash
   python app.py
   ```
   The backend will start at `http://localhost:5000`.

### 2. Frontend Setup
1. Open the `frontend/index.html` file in any modern web browser.
2. (Optional) Use a local web server (like VS Code Live Server or `python -m http.server`) for a better experience.

## Technical Details
- **Images:** Uses `Pillow` for resizing and quality reduction.
- **PDFs:** Uses `pypdf` for content stream compression.
- **DOCX:** Uses `zipfile` with `ZIP_DEFLATED` at maximum compression level.
- **API:** RESTful API with endpoints for upload, compression, and download.
- **Storage:** Temporary storage for uploaded and compressed files in `backend/uploads` and `backend/compressed`.
