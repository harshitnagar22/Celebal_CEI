from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.api.routes import router as api_router
from src.core.config import config
import uvicorn
import os

app = FastAPI(
    title="Memory-Augmented Chatbot",
    version="1.0.0"
)

# setup cors so we don't get blocked
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load the api routes
app.include_router(api_router, prefix="/api/v1")

# serve the frontend files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    # just serve the index.html on the root path
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
