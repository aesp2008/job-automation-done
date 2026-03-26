from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from backend.app.db.session import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    source = Column(String(100), nullable=False, default="fake")
    external_id = Column(String(255), nullable=False, index=True)
    url = Column(String(1024), nullable=True)
    relevance_score = Column(Float, nullable=True)
    relevance_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

