from fastapi import APIRouter, Depends, HTTPException
from serverRouter.core.security import verify_api_key  # သင့် project ၏ API key verification dependency
from serverRouter.core.state import active_providers

router = APIRouter(prefix="/v1/models", tags=["models"])

@router.get("", dependencies=[Depends(verify_api_key)])
async def list_models():
    try:
        all_models = []
        for provider_enum, provider_obj in active_providers.items():
            if provider_obj and hasattr(provider_obj, "get_models"):
                try:
                    models = provider_obj.get_models()
                    all_models.extend(models)
                except Exception as e:
                    print(f"[WARNING] Failed to fetch models from {provider_enum}: {e}")
        
        return {"object": "list", "data": all_models}
    except Exception as e:
        print(f"[ERROR] Error in list_models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
