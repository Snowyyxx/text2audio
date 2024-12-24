import os
import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI
from dotenv import load_dotenv
import uuid
from termcolor import colored
import webbrowser
import uvicorn
import aiofiles

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Create static folder if it doesn't exist
os.makedirs("static", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_speech(text: str) -> str:
    """Generate speech from text using OpenAI API"""
    try:
        print(colored(f"Generating speech for text: {text}", "cyan"))
        
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Generate unique filename
        filename = f"static/audio/speech_{uuid.uuid4()}.mp3"
        
        # Save the audio file - response.content is already bytes, no need to await
        async with aiofiles.open(filename, 'wb') as f:
            await f.write(response.content)
        
        print(colored(f"Audio file saved: {filename}", "green"))
        return filename
    
    except Exception as e:
        print(colored(f"Error generating speech: {str(e)}", "red"))
        raise

@app.get("/")
async def home(request: Request):
    """Render home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/generate")
async def generate(text: str = Form(...)):
    """Generate speech from text"""
    try:
        audio_path = await generate_speech(text)
        return JSONResponse({
            "status": "success",
            "audio_path": f"/{audio_path}"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

def open_browser():
    """Open browser after server starts"""
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    # Open browser after server starts
    asyncio.get_event_loop().run_in_executor(None, open_browser)
    uvicorn.run("agent:app", host="0.0.0.0", port=8000, reload=True) 