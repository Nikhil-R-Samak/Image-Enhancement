from fastapi import FastAPI, UploadFile, File,Form,HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
from Image_Enhancement import ImageEnhancer

app = FastAPI(title="Image Enhancement API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static directories
app.mount("/saved_results", StaticFiles(directory="saved_results"), name="saved_results")

@app.post("/enhance")
async def enhance_image(
    file: UploadFile = File(...),
    scale: int = Form(..., description="Enhancement scale (2, 4, or 8)")
    ):

    if scale not in [2, 3, 4, 8]:
        raise HTTPException(status_code=400, detail="Scale must be 2, 3, 4, or 8")


    session_id = str(uuid.uuid4())[:8]
    input_dir = f"temp/{session_id}/input"
    os.makedirs(input_dir, exist_ok=True)

    input_path = os.path.join(input_dir, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    enhancer = ImageEnhancer(tile_size=1024)
    output_path = enhancer.enhance(input_path, scale = scale)
    output_url = f"/{output_path.replace(os.sep, '/')}" if not output_path.startswith("/") else output_path

    return {"success_status": True, "message":"Enhancement complete", "output_path": output_url}