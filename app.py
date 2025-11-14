from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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

# Serve output files
app.mount("/saved_results", StaticFiles(directory="saved_results"), name="saved_results")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")

@app.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    file_path = f"saved_results/{session_id}/{filename}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="image/png", filename=filename)


@app.post("/enhance")
async def enhance_image(
    file: UploadFile = File(...),
    scale: int = Form(...)
):

    if scale not in [2, 3, 4, 8]:
        raise HTTPException(status_code=400, detail="Scale must be 2, 3, 4, or 8")

    # Create session
    session_id = str(uuid.uuid4())[:8]
    input_dir = f"temp/{session_id}"
    os.makedirs(input_dir, exist_ok=True)

    # Save uploaded file
    input_path = os.path.join(input_dir, file.filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Enhance
    enhancer = ImageEnhancer(tile_size=1024)
    output_path = enhancer.enhance(input_path, scale=scale)

    # Convert path to use forward slashes
    output_dir = f"saved_results/{session_id}"
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(output_path)
    final_output_path = os.path.join(output_dir, filename)
    os.replace(output_path, final_output_path)

    final_output_path = final_output_path.replace("\\", "/")

    return {
        "success": True,
        "message": "Enhancement complete",
        "output_url": f"/{final_output_path}",
        "download_url": f"/download/{session_id}/{filename}"
    }