from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy import select

from app.schemas.podcast import PodcastItem,  PodcastGeneratedListResponse
from app.schemas.podcast import PodcastDetailResponse
from app.models.podcast import Podcast
from app.llm_providers.base import generate_text_stream
from typing import AsyncGenerator,List



async def list_generated_podcasts(db: AsyncSession) -> PodcastGeneratedListResponse:
    from sqlalchemy import desc
    stmt = select(Podcast).order_by(desc(Podcast.created_at))
    result = await db.execute(stmt)
    podcasts = result.scalars().all()
    items = [PodcastItem(
        id=p.id,
        content=p.content,
        voice_ids=p.voice_ids,
        content_type=p.content_type,
        transcript=p.transcript,
        title=p.title,
        created_at=p.created_at.strftime("%Y-%m-%d %H:%M:%S")
    ) for p in podcasts]
    return PodcastGeneratedListResponse(total=len(items), items=items)

async def get_podcast_detail(db: AsyncSession, podcast_id: int) -> PodcastDetailResponse:
    from sqlalchemy import select
    stmt = select(Podcast).where(Podcast.id == podcast_id)
    result = await db.execute(stmt)
    podcast = result.scalar_one_or_none()
    if not podcast:
        return None
    return PodcastDetailResponse(
        id=podcast.id,
        content=podcast.content,
        voice_ids=podcast.voice_ids,
        transcript=podcast.transcript,
        content_type=podcast.content_type,
        title=podcast.title
    )






# async def save_generated_podcast(db: AsyncSession, content: str, voice_ids: str, tags: str, transcript: str, content_type: str, title: str):
#     podcast = Podcast(
#         content=content,
#         voice_ids=voice_ids,
#         transcript=transcript,
#         content_type=content_type,
#         title=title
#     )
#     db.add(podcast)
#     await db.commit()

async def generate_script_stream(
    content: str, 
    contentType: str = None, 
    voices: List[str] = [],
    db: AsyncSession = None,
    language: str = "中文"
) -> AsyncGenerator[str, None]:
    """流式生成播客脚本"""
    
    # 调用generate_text_stream函数
    async for text_chunk in generate_text_stream(content, contentType, voices, target_language=language, db=db):
        yield text_chunk
