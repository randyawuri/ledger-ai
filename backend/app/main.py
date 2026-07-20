from fastapi import FastAPI

app = FastAPI(title="LedgerAI")


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }