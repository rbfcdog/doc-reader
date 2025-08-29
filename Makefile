run:
	uvicorn app.backend.main:app --reload --port 8000 &
	streamlit run app/frontend/app.py --server.port 8501