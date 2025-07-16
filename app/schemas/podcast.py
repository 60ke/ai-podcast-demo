from pydantic import BaseModel, Field
from typing import List, Optional

# class PodcastGenerateRequest(BaseModel):
#     content: str = Field(..., description="播客内容")
#     voice_ids: List[int] = Field(..., min_items=1, description="播客音色素材ID列表，至少1个")
#     tags: str = Field(..., description="播客标签")

class PodcastGenerateResponse(BaseModel):
    task_id: int = Field(..., description="播客生成任务ID")
    status: str = Field(..., description="任务状态")
    message: Optional[str] = Field(None, description="提示信息")

class PodcastItem(BaseModel):
    id: int = Field(..., description="任务ID")
    content: str = Field(..., description="播客内容")
    voice_ids: str = Field(..., description="播客音色素材ID列表，逗号分隔")
    content_type: str = Field(..., description="播客内容标签")
    title: str = Field(..., description="播客标题")
    created_at: Optional[str] = Field(None, description="创建时间")
    transcript: Optional[str] = Field(None, description="播客完整脚本")

class PodcastListResponse(BaseModel):
    total: int = Field(..., description="总数")
    items: List[PodcastItem] = Field(..., description="任务列表")








class PodcastDetailResponse(BaseModel):
    id: int = Field(..., description="播客ID")
    content: str = Field(..., description="播客内容摘要")
    voice_ids: str = Field(..., description="播客音色素材ID列表，逗号分隔")
    content_type: str = Field(..., description="播客内容标签")
    transcript: Optional[str] = Field(None, description="播客完整脚本")
    title: str = Field(..., description="播客标题")



class ScriptGenerateRequest(BaseModel):
    content: str = Field(..., description="播客内容提示")
    language: str = Field(..., description="目标语言")
    voices: List[str] = Field(..., description="音色素材ID列表")
    contentType: str = Field(..., description="内容类型")
    timestamp: str = Field(..., description="时间戳")


class PodcastGeneratedListResponse(BaseModel):
    total: int = Field(..., description="总数")
    items: List[PodcastItem] = Field(..., description="播客列表")