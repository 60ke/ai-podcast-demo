from pydantic import BaseModel, Field
from typing import List, Optional

class PodcastGenerateRequest(BaseModel):
    content: str = Field(..., description="播客内容")
    voice_ids: List[int] = Field(..., min_items=1, description="播客音色素材ID列表，至少1个")
    tags: str = Field(..., description="播客标签")

class PodcastGenerateResponse(BaseModel):
    task_id: int = Field(..., description="播客生成任务ID")
    status: str = Field(..., description="任务状态")
    message: Optional[str] = Field(None, description="提示信息")

class PodcastTaskItem(BaseModel):
    id: int = Field(..., description="任务ID")
    content: str = Field(..., description="播客内容")
    voice_ids: str = Field(..., description="播客音色素材ID列表，逗号分隔")
    tags: str = Field(..., description="播客标签")
    status: str = Field(..., description="任务状态")
    user_id: int = Field(..., description="用户ID")

class PodcastListResponse(BaseModel):
    total: int = Field(..., description="总数")
    items: List[PodcastTaskItem] = Field(..., description="任务列表")

class PodcastRecommendRequest(BaseModel):
    scene_tag: str = Field(..., description="用户场景标签")
    limit: int = Field(10, description="推荐条数")

class PodcastRecommendResponse(BaseModel):
    items: List[PodcastTaskItem] = Field(..., description="推荐任务列表")

class PodcastCommentItem(BaseModel):
    id: int = Field(..., description="评论ID")
    podcast_id: int = Field(..., description="播客ID")
    user_id: int = Field(..., description="用户ID")
    content: str = Field(..., description="评论内容")

class PodcastItem(BaseModel):
    id: int = Field(..., description="播客ID")
    user_id: int = Field(..., description="用户ID")
    content: str = Field(..., description="播客内容摘要")
    voice_ids: str = Field(..., description="播客音色素材ID列表，逗号分隔")
    tags: str = Field(..., description="播客标签")
    mp3_url: str = Field(..., description="播客音频URL")
    transcript: Optional[str] = Field(None, description="播客完整脚本")
    ai_tags: Optional[str] = Field(None, description="AI标签/内容类型")
    duration: Optional[int] = Field(None, description="时长（秒）")
    like_count: int = Field(..., description="点赞数")

class PodcastGeneratedListResponse(BaseModel):
    total: int = Field(..., description="总数")
    items: List[PodcastItem] = Field(..., description="播客列表")

class PodcastCommentPageResponse(BaseModel):
    total: int = Field(..., description="评论总数")
    items: List[PodcastCommentItem] = Field(..., description="评论列表")

class PodcastDetailResponse(BaseModel):
    id: int = Field(..., description="播客ID")
    user_id: int = Field(..., description="用户ID")
    content: str = Field(..., description="播客内容摘要")
    voice_ids: str = Field(..., description="播客音色素材ID列表，逗号分隔")
    tags: str = Field(..., description="播客标签")
    mp3_url: str = Field(..., description="播客音频URL")
    transcript: Optional[str] = Field(None, description="播客完整脚本")
    ai_tags: Optional[str] = Field(None, description="AI标签/内容类型")
    duration: Optional[int] = Field(None, description="时长（秒）")
    like_count: int = Field(..., description="点赞数")

class PodcastCommentCreateRequest(BaseModel):
    podcast_id: int = Field(..., description="播客ID")
    content: str = Field(..., description="评论内容")

class PodcastCommentCreateResponse(BaseModel):
    id: int = Field(..., description="评论ID")
    podcast_id: int = Field(..., description="播客ID")
    user_id: int = Field(..., description="用户ID")
    content: str = Field(..., description="评论内容")

class PodcastLikeRequest(BaseModel):
    podcast_id: int = Field(..., description="播客ID")

class PodcastLikeResponse(BaseModel):
    podcast_id: int = Field(..., description="播客ID")
    like_count: int = Field(..., description="点赞数")



class ScriptGenerateRequest(BaseModel):
    content: str = Field(..., description="播客内容提示")
    language: str = Field(..., description="目标语言")
    voices: List[str] = Field(..., description="音色素材ID列表")
    contentType: str = Field(..., description="内容类型")
    timestamp: str = Field(..., description="时间戳")
