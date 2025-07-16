import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.database import AsyncSessionLocal
from app.models.podcast_task import PodcastTask, Podcast
from app.services.podcast_service import update_task_status, save_generated_podcast
# from app.llm_providers import get_llm_provider  # 预留多服务商适配

async def process_pending_tasks():
    async with AsyncSessionLocal() as db:
        stmt = select(PodcastTask).where(PodcastTask.status == "pending")
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        for task in tasks:
            try:
                # 1. 更新任务状态为running
                await update_task_status(db, task.id, "running")
                # 2. 调用LLM生成内容（此处用mock，后续接入LangChain和TTS）
                ai_content = f"AI生成内容:{task.content}"
                mp3_url = f"https://mock-audio/{task.id}.mp3"
                transcript = f"Transcript for {task.content}"
                ai_tags = "AI,播客"
                duration = 60
                # 3. 写入Podcast表
                await save_generated_podcast(db, task, mp3_url, transcript, ai_tags, duration)
                # 4. 更新任务状态为success
                await update_task_status(db, task.id, "success")
            except Exception as e:
                logging.error(f"任务{task.id}生成失败: {e}")
                await update_task_status(db, task.id, "failed")
