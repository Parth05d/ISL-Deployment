from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from service import inference_service

app = FastAPI()

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set this to the specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "ISL Connect API is running"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    file_path = None
    try:
        # Save uploaded file
        file_extension = file.filename.split(".")[-1] if file.filename else "webm"
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"[INFO] File saved to {file_path}")
        
        # Run inference
        result = inference_service.process_video(file_path)
        
        # Check for inference errors
        if "error" in result:
             raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup uploaded file
        if file_path and os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
