from fastapi import FastAPI

app = FastAPI(title="Carpool API", 
              description="API for carpool management",
              version="0.1.0")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Carpool API is healthy!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
