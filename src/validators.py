from datetime import datetime
from pydantic import BaseModel


class ContentItem(BaseModel):
  id: int
  title: str
  url: str
  description: str
  date: datetime
  source_id: int
