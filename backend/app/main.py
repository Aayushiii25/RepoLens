from fastapi import FastAPI

app = FastAPI(
    title="RepoLens API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "RepoLens API Running 🚀"}
