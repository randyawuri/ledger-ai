from fastapi import FastAPI

app = FastAPI(
    title="LedgerAI API",
    version="1.0.0",
    description="AI-powered personal financial intelligence platform"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to LedgerAI API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }