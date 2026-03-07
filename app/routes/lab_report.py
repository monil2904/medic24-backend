from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.middleware.auth import get_current_user
from app.services.storage_service import upload_file
from app.services.lab_parser import parse_lab_report
from app.models.ensemble import ensemble_query
from app.schemas import LabReportResponse, LabReportTest
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import uuid

router = APIRouter()

LAB_RATE_LIMITS = {
    "free": 0,
    "basic": 0,
    "pro": 10,
    "medical_pro": 999
}

@router.post("/upload", response_model=LabReportResponse)
async def upload_lab_report(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["id"])
    plan = current_user.get("subscription_plan", "free")
    
    if LAB_RATE_LIMITS.get(plan, 0) == 0:
        raise HTTPException(status_code=403, detail="Lab report analysis requires pro plan or higher")
        
    # Max size 20MB
    MAX_SIZE = 20 * 1024 * 1024
    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 20MB limit")
        
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if ext not in ["pdf", "jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Only PDF, JPEG, and PNG are supported")
        
    # Upload to GCS
    filename = f"labs/{user_id}_{uuid.uuid4()}.{ext}"
    try:
        gcs_url = await upload_file(file_bytes, filename, file.content_type)
    except Exception as e:
        print(f"GCS Upload Error: {e}")
        # Continue even if backup fails for reliability during dev, though production might halt
        pass
    
    # Extract text
    raw_text = ""
    try:
        if ext == "pdf":
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                raw_text += page.get_text()
        else:
            image = Image.open(io.BytesIO(file_bytes))
            raw_text = pytesseract.image_to_string(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
        
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the document")
        
    # Parse with lab_parser
    parsed_results = parse_lab_report(raw_text)
    
    # Count stats
    total_tests = len(parsed_results)
    abnormal_count = sum(1 for test in parsed_results if test["flag"] in ["HIGH", "LOW", "CRITICAL"])
    
    # Query ensemble
    query = f"Interpret this extracted lab report data and provide clinical insights:\n{parsed_results}"
    ensemble_res = await ensemble_query(query, "clinical")
    
    # Summary
    if abnormal_count > 0:
        summary = f"Analyzed {total_tests} tests. Found {abnormal_count} abnormal values that need attention."
    elif total_tests > 0:
        summary = f"Analyzed {total_tests} tests. All values appear to be within normal ranges."
    else:
        summary = "Could not parse specific test values from the document. Providing general interpretation based on available text."
    
    pydantic_results = [LabReportTest(**test) for test in parsed_results]
    
    return LabReportResponse(
        parsed_results=pydantic_results,
        ensemble_interpretation=ensemble_res.get("ensemble_response", ""),
        summary=summary,
        abnormal_count=abnormal_count,
        total_tests=total_tests,
        confidence=float(ensemble_res.get("confidence", 0.0))
    )
