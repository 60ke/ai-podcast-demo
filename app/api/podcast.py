import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.podcast import PodcastGenerateRequest, PodcastGenerateResponse, PodcastListResponse, PodcastRecommendRequest, PodcastRecommendResponse, PodcastGeneratedListResponse, PodcastDetailResponse, PodcastCommentPageResponse, PodcastCommentCreateRequest, PodcastCommentCreateResponse, PodcastLikeRequest, PodcastLikeResponse
from app.db.database import get_db
from app.services.podcast_service import create_podcast_task, list_podcast_tasks, recommend_podcast_tasks, list_generated_podcasts, get_podcast_detail, get_podcast_comments, create_podcast_comment, like_podcast, delete_podcast_comment
from fastapi.responses import StreamingResponse
from app.schemas.podcast import ScriptGenerateRequest
from app.services.podcast_service import generate_script_stream

router = APIRouter()

@router.post("/generate", response_model=PodcastGenerateResponse)
async def generate_podcast(
    req: PodcastGenerateRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user_id = request.state.user_id
    task = await create_podcast_task(db, req, user_id)
    if not task:
        raise HTTPException(status_code=500, detail="任务创建失败")
    return PodcastGenerateResponse(task_id=task.id, status=task.status, message="任务已创建")



@router.post("/generate_script")
async def generate_script(
    req: ScriptGenerateRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    使用SSE流式返回生成的播客脚本，并将生成的内容保存到数据库
    """
    # 获取当前用户ID
    user_id = getattr(request.state, "user_id", None)
    
    async def event_generator():
        async for text_chunk in generate_script_stream(
            req.content, 
            req.contentType, 
            req.voices,
            db=db,
            user_id=user_id,
            language=req.language
        ):
            # 格式化为SSE事件
            json_data = json.dumps({"text": text_chunk}, ensure_ascii=False)
            yield f"data: {json_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )




@router.get("/list", response_model=PodcastListResponse)
async def get_podcast_list(
    all: bool = Query(False, description="是否查询所有用户的播客"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user_id = None
    return await list_podcast_tasks(db, user_id)

@router.post("/recommend", response_model=PodcastRecommendResponse)
async def recommend_podcast(
    req: PodcastRecommendRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user_id = request.state.user_id
    items = await recommend_podcast_tasks(db, user_id, req.scene_tag, req.limit)
    return PodcastRecommendResponse(items=items)

@router.get("/generated", response_model=PodcastGeneratedListResponse)
async def get_generated_podcast_list(
    all: bool = Query(False, description="是否查询所有用户的已生成播客"),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user_id = None if all else request.state.user_id
    return await list_generated_podcasts(db, user_id)

@router.get("/detail", response_model=PodcastDetailResponse)
async def get_podcast_detail_api(
    podcast_id: int,
    db: AsyncSession = Depends(get_db)
):
    detail = await get_podcast_detail(db, podcast_id)
    if not detail:
        raise HTTPException(status_code=404, detail="播客不存在")
    return detail

@router.get("/comments", response_model=PodcastCommentPageResponse)
async def get_podcast_comments_api(
    podcast_id: int,
    page: int = Query(1, ge=1, description="评论页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页评论数"),
    db: AsyncSession = Depends(get_db)
):
    return await get_podcast_comments(db, podcast_id, page, page_size)

@router.post("/comment", response_model=PodcastCommentCreateResponse)
async def create_podcast_comment_api(
    req: PodcastCommentCreateRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user_id = request.state.user_id
    comment = await create_podcast_comment(db, req.podcast_id, user_id, req.content)
    return PodcastCommentCreateResponse(
        id=comment.id,
        podcast_id=comment.podcast_id,
        user_id=comment.user_id,
        content=comment.content
    )

@router.post("/like", response_model=PodcastLikeResponse)
async def like_podcast_api(
    req: PodcastLikeRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user_id = request.state.user_id
    podcast, liked = await like_podcast(db, req.podcast_id, user_id)
    if not podcast:
        raise HTTPException(status_code=404, detail="播客不存在")
    if not liked:
        raise HTTPException(status_code=400, detail="请勿重复点赞")
    return PodcastLikeResponse(podcast_id=podcast.id, like_count=podcast.like_count)

@router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_podcast_comment_api(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    user_id = request.state.user_id
    ok = await delete_podcast_comment(db, comment_id, user_id)
    if not ok:
        raise HTTPException(status_code=403, detail="无权删除或评论不存在")
