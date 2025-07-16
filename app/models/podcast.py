from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import func

Base = declarative_base()



class Podcast(Base):
    __tablename__ = "podcast"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text, nullable=False)
    voice_ids = Column(String(255), nullable=False)
    content_type = Column(String(255), nullable=False)
    transcript = Column(Text, nullable=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

