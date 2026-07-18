from fastapi import FastAPI

app = FastAPI(title= "LedgerAI API")

@app.get("/")
def root():
    return {"message": "LedgerAI API"}