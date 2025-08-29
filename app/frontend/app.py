import streamlit as st
import requests
import json

st.title("Textract Frontend (Streamlit + FastAPI)")

file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "pdf"])

# Session state to persist between reruns
if "textract_result" not in st.session_state:
    st.session_state.textract_result = None

if file:
    if file.type == "application/pdf":
        st.text("PDF files are not supported for viewing.")
    else:
        st.image(file, caption="Uploaded Image")

    if st.button("Send to Textract"):
        with st.spinner("Sending to backend..."):
            files = {"file": (file.name, file, file.type)}
            try:    
                response = requests.post("http://localhost:8000/detect-text", files=files)
                response.raise_for_status()
                st.session_state.textract_result = response.json()
                st.success("Textract succeeded.")
            except Exception as e:
                st.error(f"Textract error: {e}")
                st.session_state.textract_result = None

    if st.button("Clear"):
        print(st.session_state.textract_result)

# Only show this part if we have valid data
if st.session_state.textract_result:
    st.subheader("Textract Result (Raw JSON):")
    st.text_area("Copyable JSON", json.dumps(st.session_state.textract_result, indent=2), height=400)

    if st.button("Save in Sheets"):
        with st.spinner("Saving to Google Sheets..."):
            try:
                sheet_response = requests.post(
                    "http://localhost:8000/save-in-sheets",
                    json=st.session_state.textract_result
                )
                sheet_response.raise_for_status()
                st.success("Data saved in Google Sheets!")
            except Exception as e:
                st.error(f"Failed to save in Sheets: {e}")
