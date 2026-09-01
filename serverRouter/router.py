from contextlib import asynccontextmanager
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

active_providers = {}

def initialize_providers():
    providers_list = [
        ("OPENAI", OpenAIProvider),
        ("GEMINI", GeminiProvider),
        ("TOGETHER", TogetherAIProvider),
        ("STABILITY", StableDiffusionProvider),
        ("STABLE_DIFFUSION", StableDiffusionProvider),
        ("ANTHROPIC", AnthropicProvider),
        ("DEEPSEEK", DeepSeekProvider),
    ]

    for enum_name, provider_cls in providers_list:
        try:
            if hasattr(ModelProvider, enum_name):
                provider_enum = getattr(ModelProvider, enum_name)
                if provider_enum not in active_providers:
                    active_providers[provider_enum] = provider_cls()
                    print(f"[INFO] Successfully initialized {enum_name}")
        except Exception as e:
            print(f"[WARNING] Skipping {enum_name} due to initialization error: {e}")

# App စတင်ချိန်နှင့် ပိတ်ချိန် Lifespan သတ်မှတ်ခြင်း
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: App စတင်ချိန်တွင် Provider များ Init လုပ်မည်
    initialize_providers()
    yield
    # Shutdown: ပိတ်ချိန် လုပ်ဆောင်ချက်များ (လိုအပ်ပါက)

app = FastAPI(title="OmniLLM", description="One Key, One API, Hundreds of Models", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(model_routes.router)
app.include_router(completion_routes.router)
app.include_router(smart_routes.router)
app.include_router(reasoning_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to OmniLLM!"}
