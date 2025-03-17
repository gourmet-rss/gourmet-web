from datetime import datetime
from pydantic import BaseModel


class ContentItem(BaseModel):
  id: int
  title: str
  url: str
  description: str
  image_url: str | None
  image_text: str | None
  content_type: str | None
  date: datetime
  source_id: int


class UserContentItem(ContentItem):
  rating: int
  source_url: str


class Feedback(BaseModel):
  content_id: int
  rating: int
