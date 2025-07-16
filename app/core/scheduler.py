from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from app.tasks.podcast_task import process_pending_tasks

scheduler = AsyncIOScheduler()

# 示例任务：实际播客生成任务将在tasks/podcast_task.py实现
async def example_job():
    logging.info("调度器心跳：example_job 执行")

# 启动调度器并注册任务

def start_scheduler():
    scheduler.start()
    # 每30秒执行一次播客生成任务
    scheduler.add_job(process_pending_tasks, IntervalTrigger(seconds=30), id="process_podcast_tasks", replace_existing=True)
