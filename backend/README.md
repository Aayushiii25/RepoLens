# RepoLens Backend API

This is the production-ready FastAPI backend for RepoLens.

## Development Setup

1. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Running the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Interactive Documentation**:
   Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to view the API documentation.
