# Document Reader

A full-stack document processing application that extracts structured data from invoices and documents using AWS Textract and stores the results in Google Sheets.

## Features

- **Document Text Extraction**: Upload images (JPG, JPEG, PNG) or PDF files for text extraction
- **Invoice Data Processing**: Automatically extracts key invoice information including:
  - CNPJ (Company identifier)
  - Total value/price
  - Company name
  - Invoice date
  - DANFE number
  - Invoice series number
- **PDF Support**: Converts PDF files to images for processing (processes up to 2 pages)
- **Google Sheets Integration**: Saves extracted data directly to Google Sheets
- **User-friendly Interface**: Streamlit frontend with drag-and-drop file upload

## Architecture

The application consists of two main components:

### Backend (FastAPI)

- **Location**: `app/backend/main.py`
- **Port**: 8000
- **Features**:
  - RESTful API endpoints for document processing
  - AWS Textract integration for text extraction
  - Google Sheets API integration for data storage
  - PDF to image conversion support
  - CORS enabled for frontend communication

### Frontend (Streamlit)

- **Location**: `app/frontend/app.py`
- **Port**: 8501
- **Features**:
  - File upload interface
  - Real-time processing status
  - JSON result visualization
  - One-click Google Sheets export

## Prerequisites

1. **AWS Account**: Configure AWS credentials for Textract access
2. **Google Cloud Project**: Set up Google Sheets API access
3. **Python 3.10+**: Required for running the application

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd doc-reader
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Secrets

#### AWS Credentials

Configure your AWS credentials using one of these methods:

- AWS CLI: `aws configure`
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- IAM roles (if running on EC2)

Ensure your AWS account has Textract permissions.

#### Google Sheets API

1. Create a service account in Google Cloud Console
2. Download the service account JSON file
3. Place it at `secrets/primal-bonbon-465618-g6-3f9bb8f68cc9.json`
4. Share your target Google Sheet with the service account email

### 4. Additional Dependencies for PDF Processing

```bash
# For PDF to image conversion
pip install pdf2image
pip install boto3
pip install google-api-python-client google-auth
```

## Running the Application

### Option 1: Using Make (Recommended)

```bash
make run
```

### Option 2: Manual Startup

```bash
# Start backend
uvicorn app.backend.main:app --reload --port 8000 &

# Start frontend
streamlit run app/frontend/app.py --server.port 8501
```

### Option 3: Using Docker

```bash
docker build -t doc-reader .
docker run -p 8000:8000 -p 8501:8501 doc-reader
```

## Usage

1. **Access the Application**: Open your browser and navigate to `http://localhost:8501`
2. **Upload Document**: Use the file uploader to select an image or PDF file
3. **Process Document**: Click "Send to Textract" to extract text and data
4. **Review Results**: View the extracted data in JSON format
5. **Save to Sheets**: Click "Save in Sheets" to export data to Google Sheets

## API Endpoints

### POST `/detect-text`

Extracts text and structured data from uploaded documents.

**Request**: Multipart form data with file
**Response**: JSON array with extracted data

### POST `/save-in-sheets`

Saves extracted data to Google Sheets.

**Request**: JSON array with document data
**Response**: Success status and updated cell count

## Configuration

### Google Sheets

- **Spreadsheet ID**: `1QwLgssBCroBvTLlVJ_6NQk0G_WbfhhBk3Y4L730_zRM`
- **Range**: `Sheet1!A1`
- **Service Account File**: `secrets/primal-bonbon-465618-g6-3f9bb8f68cc9.json`

### Textract Queries

The application extracts the following fields from invoices:

- CNPJ number
- Total value (R$)
- Company name
- Invoice date
- DANFE number
- Invoice series

## File Structure

```
doc-reader/
├── app/
│   ├── backend/
│   │   └── main.py          # FastAPI backend
│   └── frontend/
│       └── app.py           # Streamlit frontend
├── secrets/
│   ├── invoice.jpeg         # Sample invoice
│   └── primal-bonbon-*.json # Google service account key
├── Dockerfile               # Container configuration
├── Makefile                # Build and run commands
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### Common Issues

1. **AWS Textract Errors**: Ensure AWS credentials are properly configured and have Textract permissions
2. **Google Sheets Access**: Verify the service account has edit permissions on the target spreadsheet
3. **PDF Processing**: Large PDF files may take longer to process; only first 2 pages are processed
4. **Port Conflicts**: Ensure ports 8000 and 8501 are available

### Dependencies Issues

If you encounter issues with PDF processing:

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```
