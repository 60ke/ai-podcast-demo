import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.podcast import PodcastListResponse, PodcastDetailResponse
from app.db.database import get_db
from app.services.podcast_service import get_podcast_detail
from fastapi.responses import StreamingResponse
from app.schemas.podcast import ScriptGenerateRequest
from app.services.podcast_service import generate_script_stream
from app.schemas.podcast import PodcastGeneratedListResponse
from app.services.podcast_service import list_generated_podcasts

router = APIRouter()




@router.post("/generate_script")
async def generate_script(
    req: ScriptGenerateRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """
    使用SSE流式返回生成的播客脚本，并将生成的内容保存到数据库
    """

    
    async def event_generator():
        async for text_chunk in generate_script_stream(
            req.content, 
            req.contentType, 
            req.voices,
            db=db,
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




@router.get("/list", response_model=PodcastGeneratedListResponse)
async def get_podcast_list(
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    return await list_generated_podcasts(db)





@router.get("/detail", response_model=PodcastDetailResponse)
async def get_podcast_detail_api(
    podcast_id: int,
    db: AsyncSession = Depends(get_db)
):
    detail = await get_podcast_detail(db, podcast_id)
    if not detail:
        raise HTTPException(status_code=404, detail="播客不存在")
    return detail







