from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from serverRouter.core.config import VALID_API_KEYS
from serverRouter.core.state import active_providers

router = APIRouter(prefix="/v1/models", tags=["models"])
security = HTTPBearer()

def verify_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if token not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token

@router.get("", dependencies=[Depends(verify_key)])
async def list_models():
    try:
        all_models = []
        
        # Active providers များထံမှ Dynamic Models ဆွဲယူခြင်း
        for provider_enum, provider_obj in active_providers.items():
            if provider_obj and hasattr(provider_obj, "get_models"):
                try:
                    models = provider_obj.get_models()
                    # ရရှိလာသော model Format များကို စစ်ဆေး၍ list ထဲထည့်ခြင်း
                    if isinstance(models, list):
                        all_models.extend(models)
                except Exception as e:
                    print(f"[WARNING] Failed to fetch models from {provider_enum}: {e}")
        
        # Provider ထံမှ Models မလာသေးပါက Android Studio IDE Agent အတွက် Default Fallback ထည့်သွင်းခြင်း
        if not all_models:
            all_models = [
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
        
        return {"object": "list", "data": all_models}
        
    except Exception as e:
        print(f"[ERROR] Error in list_models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
