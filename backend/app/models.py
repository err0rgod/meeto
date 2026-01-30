from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)   
    title = Column(String, default="Untitled Meeting")
    timestamp = Column(DateTime, default=datetime.utcnow)
    audio_path = Column(String, nullable=True)
    transcript_text = Column(Text, nullable=True)
    summary_text = Column(Text, nullable=True)
    status = Column(String, default="PROCESSING") # PROCESSING, COMPLETED, ERROR
    
    action_items = relationship("ActionItem", back_populates="meeting")

class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    description = Column(String)
    owner = Column(String, nullable=True)
    priority = Column(String, default="Medium")
    jira_ticket_key = Column(String, nullable=True)
    jira_ticket_url = Column(String, nullable=True)
    
    meeting = relationship("Meeting", back_populates="action_items")
