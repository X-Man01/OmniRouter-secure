from typing import List, Optional, Dict, Literal, Union, Any
from pydantic import BaseModel, Field
from enum import Enum
from collections.abc import Mapping
from sse_starlette.sse import EventSourceResponse

# Type alias for streaming responses
ChatCompletionGenerator = EventSourceResponse
ChatReasoningGenerator = EventSourceResponse

class ModelProvider(str, Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    TOGETHER = "together"
    STABLEDIFFUSION = "stablediffusion"

## Chat Completion Models
class ChatMessage(BaseModel):
    """Represents a single message in a chat conversation"""
    role: str = Field(..., description="Role of the message sender")
    content: Union[str, List[Any], None] = Field(default="", description="Content of the message")
    name: Optional[str] = None

    class Config:
        extra = "ignore"  # Multimodal သို့မဟုတ် metadata ပို့လာပါက လက်ခံရန်

class ChatCompletionRequest(BaseModel):
    """Input parameters for a chat completion request (OpenAI-compatible)"""
    model: str = Field(..., description="Name of the model to use")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(default=1.0)
    max_tokens: Optional[int] = Field(default=None)
    stream: Optional[bool] = Field(default=False)
    top_p: Optional[float] = Field(default=1.0)
    n: Optional[int] = Field(default=1)
    presence_penalty: Optional[float] = Field(default=0.0)
    frequency_penalty: Optional[float] = Field(default=0.0)
    user: Optional[str] = None

    class Config:
        extra = "ignore"  # Android Studio Agent ၏ Extra Request Parameter များကို Auto-bypass လုပ်ရန်

class ChatCompletionResponse(BaseModel):
    """Response from a chat completion request (OpenAI Specs)"""
    id: Optional[str] = "chatcmpl-omni"
    object: Optional[str] = "chat.completion"
    created: Optional[int] = 1677652288
    model: str = Field(..., description="Name of the model used")
    choices: Optional[List[Any]] = None
    content: Optional[str] = None
    provider: Optional[str] = "omnirouter"
    usage: Dict[str, int] = Field(
        default_factory=lambda: {"total_tokens": 0},
        description="Token usage statistics"
    )

    class Config:
        extra = "ignore"

## Reasoning Models
class ReasoningEffort(str, Enum):
    """Level of reasoning effort for reasoning models"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ReasoningTokenUsage(BaseModel):
    """Detailed token usage for reasoning models"""
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    reasoning_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)

class ChatReasoningRequest(BaseModel):
    """Input parameters for a reasoning chat completion request"""
    model: str = Field(..., description="Name of the model to use")
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    reasoning_effort: ReasoningEffort = Field(default=ReasoningEffort.MEDIUM)
    max_tokens: Optional[int] = Field(default=None)
    stream: bool = Field(default=False)
    temperature: float = Field(default=1.0)

    class Config:
        extra = "ignore"

class ChatReasoningResponse(BaseModel):
    """Response from a reasoning chat completion request"""
    model: str = Field(...)
    content: str = Field(...)
    provider: str = Field(...)
    usage: ReasoningTokenUsage = Field(default_factory=ReasoningTokenUsage)

## Image Generation Models
class ImageSize(str, Enum):
    """Supported image sizes"""
    SMALL = "256x256"
    MEDIUM = "512x512"
    LARGE = "1024x1024"

class ImageGenerationRequest(BaseModel):
    """Input parameters for an image generation request"""
    prompt: str = Field(...)
    model: str = Field(default="dall-e-3")
    size: ImageSize = Field(default=ImageSize.LARGE)
    quality: Literal["standard", "hd"] = Field(default="standard")
    n: int = Field(default=1)

    class Config:
        extra = "ignore"

class ImageGenerationResponse(BaseModel):
    """Response from an image generation request"""
    urls: List[str] = Field(...)
    model: str = Field(...)
    provider: str = Field(...)

class BenchmarkScores(BaseModel, Mapping):
    MMLU: Optional[float] = Field(None)
    GPQA: Optional[float] = Field(None)
    HumanEval: Optional[float] = Field(None)
    MATH: Optional[float] = Field(None)
    BFCL: Optional[float] = Field(None)
    MGSM: Optional[float] = Field(None)

    class Config:
        validate_assignment = True
        extra = "ignore"

    def __getitem__(self, key: str) -> Optional[float]:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Optional[float]) -> None:
        setattr(self, key, value)

    def __iter__(self):
        return iter(self.__fields__)

    def __len__(self) -> int:
        return len(self.__fields__)

    def update(self, other: Dict[str, Optional[float]]) -> None:
        for key, value in other.items():
            self[key] = value

class ModelInfo(BaseModel):
    """Information about a model"""
    name: str = Field(...)
    provider: ModelProvider = Field(...)
    description: str = Field(...)
    max_tokens: Optional[int] = Field(None)
    benchmarks: Optional[BenchmarkScores] = Field(default=None)
    tokenCost: Optional[float] = Field(default=None)
    latency: Optional[float] = Field(default=None)
    extended_thinking: Optional[bool] = Field(default=False)
    thinking_threshold: Optional[float] = Field(default=0.5)
    thinking_budget: Optional[int] = Field(default=20000)

    class Config:
        extra = "ignore"

class SmartRouterRequest(BaseModel):
    messages: list[ChatMessage] = Field(...)
    max_latency: str = Field(...)
    max_cost: str = Field(...)
    model_list: list = Field(...)

    class Config:
        extra = "ignore"
