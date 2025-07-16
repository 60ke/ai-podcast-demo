from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class PodcastTask(Base):
    __tablename__ = "podcast_task"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text, nullable=False)
    voice_ids = Column(String(255), nullable=False)  # 逗号分隔的ID字符串
    tags = Column(String(255), nullable=False)
    status = Column(String(32), default="pending")
    user_id = Column(Integer, nullable=False, index=True)

class Podcast(Base):
    __tablename__ = "podcast"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    voice_ids = Column(String(255), nullable=False)
    tags = Column(String(255), nullable=False)
    mp3_url = Column(String(512), nullable=False)
    transcript = Column(Text, nullable=True)
    ai_tags = Column(String(255), nullable=True)
    duration = Column(Integer, nullable=True)  # 单位：秒
    like_count = Column(Integer, default=0)
    comments = relationship("PodcastComment", back_populates="podcast")

class PodcastComment(Base):
    __tablename__ = "podcast_comment"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    podcast_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    podcast = relationship("Podcast", back_populates="comments", foreign_keys=[podcast_id], uselist=False)

class PodcastLike(Base):
    __tablename__ = "podcast_like"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    podcast_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
