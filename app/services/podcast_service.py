from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.podcast import PodcastGenerateRequest
from app.models.podcast_task import PodcastTask
from sqlalchemy import insert
from sqlalchemy import select
from app.schemas.podcast import PodcastListResponse, PodcastTaskItem
from app.models.podcast_task import Podcast, PodcastComment
from app.schemas.podcast import PodcastItem, PodcastCommentItem, PodcastGeneratedListResponse
from app.schemas.podcast import PodcastDetailResponse, PodcastCommentPageResponse
from app.models.podcast_task import PodcastLike
from app.llm_providers.base import generate_text_stream
from typing import AsyncGenerator,List

async def create_podcast_task(db: AsyncSession, req: PodcastGenerateRequest, user_id: int):
    new_task = PodcastTask(
        content=req.content,
        voice_ids=','.join(map(str, req.voice_ids)),
        tags=req.tags,
        status="pending",
        user_id=user_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

async def list_podcast_tasks(db: AsyncSession, user_id: int = None) -> PodcastListResponse:
    stmt = select(PodcastTask)
    if user_id is not None:
        stmt = stmt.where(PodcastTask.user_id == user_id)
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    items = [PodcastTaskItem(
        id=t.id,
        content=t.content,
        voice_ids=t.voice_ids,
        tags=t.tags,
        status=t.status,
        user_id=t.user_id
    ) for t in tasks]
    return PodcastListResponse(total=len(items), items=items)

async def recommend_podcast_tasks(db: AsyncSession, user_id: int, scene_tag: str, limit: int = 10):
    stmt = select(PodcastTask).where(PodcastTask.tags.like(f"%{scene_tag}%"))
    stmt = stmt.order_by(PodcastTask.id.desc()).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    items = [PodcastTaskItem(
        id=t.id,
        content=t.content,
        voice_ids=t.voice_ids,
        tags=t.tags,
        status=t.status,
        user_id=t.user_id
    ) for t in tasks]
    return items

async def list_generated_podcasts(db: AsyncSession, user_id: int = None) -> PodcastGeneratedListResponse:
    stmt = select(Podcast)
    if user_id is not None:
        stmt = stmt.where(Podcast.user_id == user_id)
    result = await db.execute(stmt)
    podcasts = result.scalars().all()
    items = [PodcastItem(
        id=p.id,
        user_id=p.user_id,
        content=p.content,
        voice_ids=p.voice_ids,
        tags=p.tags,
        mp3_url=p.mp3_url,
        transcript=p.transcript,
        ai_tags=p.ai_tags,
        duration=p.duration,
        like_count=p.like_count
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
        user_id=podcast.user_id,
        content=podcast.content,
        voice_ids=podcast.voice_ids,
        tags=podcast.tags,
        mp3_url=podcast.mp3_url,
        transcript=podcast.transcript,
        ai_tags=podcast.ai_tags,
        duration=podcast.duration,
        like_count=podcast.like_count
    )

async def get_podcast_comments(db: AsyncSession, podcast_id: int, page: int = 1, page_size: int = 10) -> PodcastCommentPageResponse:
    from sqlalchemy import select, func
    count_stmt = select(func.count(PodcastComment.id)).where(PodcastComment.podcast_id == podcast_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    comment_stmt = select(PodcastComment).where(PodcastComment.podcast_id == podcast_id)
    comment_stmt = comment_stmt.order_by(PodcastComment.id.desc()).offset((page-1)*page_size).limit(page_size)
    comment_result = await db.execute(comment_stmt)
    comments = comment_result.scalars().all()
    comment_items = [PodcastCommentItem(
        id=c.id,
        podcast_id=c.podcast_id,
        user_id=c.user_id,
        content=c.content
    ) for c in comments]
    return PodcastCommentPageResponse(total=total, items=comment_items)

async def create_podcast_comment(db: AsyncSession, podcast_id: int, user_id: int, content: str):
    comment = PodcastComment(podcast_id=podcast_id, user_id=user_id, content=content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment

async def like_podcast(db: AsyncSession, podcast_id: int, user_id: int):
    from sqlalchemy import select, update
    # 检查是否已点赞
    like_stmt = select(PodcastLike).where(PodcastLike.podcast_id == podcast_id, PodcastLike.user_id == user_id)
    like_result = await db.execute(like_stmt)
    like = like_result.scalar_one_or_none()
    if like:
        # 已点赞，直接返回当前点赞数
        result = await db.execute(select(Podcast).where(Podcast.id == podcast_id))
        podcast = result.scalar_one_or_none()
        return podcast, False
    # 新增点赞
    new_like = PodcastLike(podcast_id=podcast_id, user_id=user_id)
    db.add(new_like)
    stmt = update(Podcast).where(Podcast.id == podcast_id).values(like_count=Podcast.like_count + 1)
    await db.execute(stmt)
    await db.commit()
    # 查询最新点赞数
    result = await db.execute(select(Podcast).where(Podcast.id == podcast_id))
    podcast = result.scalar_one_or_none()
    return podcast, True

async def delete_podcast_comment(db: AsyncSession, comment_id: int, user_id: int):
    from sqlalchemy import select, delete
    stmt = select(PodcastComment).where(PodcastComment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    if not comment or comment.user_id != user_id:
        return False
    await db.execute(delete(PodcastComment).where(PodcastComment.id == comment_id))
    await db.commit()
    return True

async def update_task_status(db: AsyncSession, task_id: int, status: str):
    from sqlalchemy import update
    stmt = update(PodcastTask).where(PodcastTask.id == task_id).values(status=status)
    await db.execute(stmt)
    await db.commit()

async def save_generated_podcast(db: AsyncSession, task: PodcastTask, mp3_url: str, transcript: str, ai_tags: str, duration: int):
    podcast = Podcast(
        user_id=task.user_id,
        content=task.content,
        voice_ids=task.voice_ids,
        tags=task.tags,
        mp3_url=mp3_url,
        transcript=transcript,
        ai_tags=ai_tags,
        duration=duration,
        like_count=0
    )
    db.add(podcast)
    await db.commit()
    await db.refresh(podcast)
    return podcast

async def generate_script_stream(
    content: str, 
    contentType: str = None, 
    voices: List[str] = [],
    db: AsyncSession = None,
    user_id: int = None,
    language: str = "中文"
) -> AsyncGenerator[str, None]:
    """流式生成播客脚本"""
    
    # 调用generate_text_stream函数，传递db和user_id参数
    async for text_chunk in generate_text_stream(content, contentType, voices,target_language=language, db=db, user_id=user_id):
        yield text_chunk
