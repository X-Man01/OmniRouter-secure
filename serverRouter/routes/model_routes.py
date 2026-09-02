from fastapi import APIRouter, Depends, HTTPException, Request
from serverRouter.core.config import VALID_API_KEYS

router = APIRouter(prefix="/v1/models", tags=["models"])

def verify_key(request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    
    # Key စစ်ဆေးခြင်း
    if not token or (token not in VALID_API_KEYS and auth_header not in VALID_API_KEYS):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token

@router.get("", dependencies=[Depends(verify_key)])
async def list_models():
    # Android Studio Timeout (10s) ကျော်လွန်မသွားစေရန် တိုက်ရိုက် Instant Response ပြန်ပေးခြင်း
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "created": 1677610602,
                "owned_by": "omnirouter"
            },
            {
                "id": "gpt-4o",
                "object": "model",
                "created": 1677610602,
                "owned_by": "omnirouter"
            }
        ]
    }
