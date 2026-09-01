from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from serverRouter.core.datamodels import ModelProvider
from serverRouter.providers.anthropic.provider import AnthropicProvider
from serverRouter.providers.openai.provider import OpenAIProvider
from serverRouter.providers.gemini.provider import GeminiProvider
from serverRouter.providers.deepseek.provider import DeepSeekProvider
from serverRouter.providers.together.provider import TogetherAIProvider
from serverRouter.providers.stablediffusion.provider import StableDiffusionProvider
from serverRouter.routes import model_routes, completion_routes, smart_routes, reasoning_routes
from serverRouter.core.config import PROVIDERS


app = FastAPI(title="OmniLLM", description="One Key, One API, Hundreds of Models")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_providers = {}

def initialize_providers():
    # (Enum Name String, Class Name) အဖြစ် သတ်မှတ်ခြင်းဖြင့် Enum ရှာမတွေ့ပါက တိုက်ရိုက် Crash မဖြစ်တော့ပါ
    providers_list = [
        ("OPENAI", OpenAIProvider),
        ("GEMINI", GeminiProvider),
        ("TOGETHER", TogetherAIProvider),
        ("STABILITY", StableDiffusionProvider),
        ("STABLE_DIFFUSION", StableDiffusionProvider),  # Alt Enum Key
        ("ANTHROPIC", AnthropicProvider),
        ("DEEPSEEK", DeepSeekProvider),
    ]

    for enum_name, provider_cls in providers_list:
        try:
            # ModelProvider ထဲတွင် အဆိုပါ Enum ရှိမရှိ Safe Check လုပ်ခြင်း
            if hasattr(ModelProvider, enum_name):
                provider_enum = getattr(ModelProvider, enum_name)
                
                # ထပ်မံ initialize မလုပ်မိစေရန် စစ်ဆေးခြင်း
                if provider_enum not in active_providers:
                    active_providers[provider_enum] = provider_cls()
                    print(f"[INFO] Successfully initialized {enum_name}")
        except Exception as e:
            # Key မရှိခြင်း သို့မဟုတ် အခြား Provider Error များကို Skip လုပ်မည်
            print(f"[WARNING] Skipping {enum_name} due to initialization error: {e}")

# Initialize providers during startup
initialize_providers()

# Include routers
app.include_router(model_routes.router)
app.include_router(completion_routes.router)
app.include_router(smart_routes.router)
app.include_router(reasoning_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to OmniLLM!"}
