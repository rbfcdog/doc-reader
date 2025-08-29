from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pdf2image import convert_from_bytes
import traceback
from io import BytesIO

app = FastAPI()

# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_document(content: bytes):
    client = boto3.client('textract')

    try:
        response = client.analyze_document(
            Document={'Bytes': content},
            FeatureTypes=['QUERIES'],
            QueriesConfig={
                'Queries': [
                    {'Text': 'What is the CNPJ number (company identifier) listed in the header of the invoice?', 'Alias': 'CNPJ'},
                    {'Text': 'What is the total value of the invoice in currency (R$)?', 'Alias': 'price'},
                    {'Text': 'What is the full legal name of the company that created the invoice?', 'Alias': 'company'},
                    {'Text': 'What is the date when the invoice was created?', 'Alias': 'date'},
                    {'Text': 'What is the unique DANFE number shown on the invoice?', 'Alias': 'invoice_number'},
                    {'Text': 'What is the series number of the invoice (labeled as Serie)?', 'Alias': 'invoice_series'},
                ]
            }
        )

        query_blocks = [b for b in response['Blocks'] if b['BlockType'] == 'QUERY']
        result_blocks = [b for b in response['Blocks'] if b['BlockType'] == 'QUERY_RESULT']

        result = {}
        for query_block, result_block in zip(query_blocks, result_blocks):
            result[query_block['Query']['Alias']] = result_block.get('Text', '')

        print(result)
        return result

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=f"Textract error: {str(e)}")

@app.post("/detect-text")
async def detect_text(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if file.content_type == 'application/pdf':
            images = convert_from_bytes(content, dpi=300, fmt='png')

            image_list = []
            for img in images:
                buf = BytesIO()
                img.save(buf, format="PNG")
                image_bytes = buf.getvalue()  
                image_list.append(image_bytes)

            results = []    
            for i, img in enumerate(image_list):
                # if i == 2:
                #     break
                print(i)
                results.append(analyze_document(img))

        else:
            results = [analyze_document(content)]

        return JSONResponse(status_code=200, content=results)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


def append_spreadsheet(sheets_service, spreadsheet_id: str, range_name: str, values: list):
    body = {'values': values}

    try:
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        updated_cells = result.get("updates", {}).get("updatedCells", 0)
        return {"status": "success", "updatedCells": updated_cells}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets API error: {e}")

@app.post("/save-in-sheets")
async def save_in_sheets(data: list[dict] = None):
    if not data:
        raise HTTPException(status_code=400, detail="Missing or invalid data")

    try:
        SCOPES = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        SERVICE_ACCOUNT_FILE = 'secrets/primal-bonbon-465618-g6-3f9bb8f68cc9.json'

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        sheets_service = build('sheets', 'v4', credentials=creds)

        spreadsheet_id = "foo"
        range_name = "Sheet1!A1"

        values = [list(row.values()) for row in data]  # ensure it's a 2D list
        result = append_spreadsheet(sheets_service, spreadsheet_id, range_name, values)

        return JSONResponse(status_code=200, content=result)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
