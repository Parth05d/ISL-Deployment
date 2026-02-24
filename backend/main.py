from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import traceback  # Added for detailed logging
from service import inference_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "ISL Connect API is running", "model_loaded": inference_service.model is not None}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    file_path = None
    try:
        file_extension = file.filename.split(".")[-1] if file.filename else "webm"
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"[INFO] File saved to {file_path}. Starting inference...")
        
        # Run inference
        result = inference_service.process_video(file_path)
        
        if "error" in result:
             print(f"[ERROR] Inference logic returned: {result['error']}")
             raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        # This prints the FULL error traceback to your Render logs
        error_details = traceback.format_exc()
        print(f"[CRITICAL ERROR] Prediction failed:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
    finally:
        if file_path and os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

if __name__ == "__main__":
    import uvicorn
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)