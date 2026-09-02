from fastapi import APIRouter, Depends, HTTPException, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from serverRouter.core.config import VALID_API_KEYS
from serverRouter.core.state import active_providers

router = APIRouter(prefix="/v1/models", tags=["models"])
security = HTTPBearer(auto_error=False)

def verify_key(request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    
    # Header မပါလျှင် သို့မဟုတ် key မှားနေလျှင် query param သို့မဟုတ် raw string စစ်မည်
    if not token or token not in VALID_API_KEYS:
        # API Key တိုက်ရိုက် ရောက်မရောက် စစ်ခြင်း
        if auth_header in VALID_API_KEYS:
            token = auth_header
        else:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return token

@router.get("", dependencies=[Depends(verify_key)])
async def list_models():
    try:
        all_models = []
        for provider_enum, provider_obj in active_providers.items():
            if provider_obj and hasattr(provider_obj, "get_models"):
                try:
                    models = provider_obj.get_models()
                    if isinstance(models, list):
                        all_models.extend(models)
                except Exception as e:
                    print(f"[WARNING] Failed to fetch models from {provider_enum}: {e}")
        
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
