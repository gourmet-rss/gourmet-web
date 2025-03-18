from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional, Union, List
import json


class Media(BaseModel):
  url: str
  medium: Optional[str] = None  # e.g., "image", "video", etc.
  type: Optional[str] = None  # e.g., "image/jpeg", "video/mp4", etc.
  width: Optional[int] = None
  height: Optional[int] = None


class ContentItem(BaseModel):
  id: int
  title: str
  url: str
  description: str
  media: Optional[List[Media]] = None
  date: datetime
  source_id: int
  content_type: str

  @field_validator("media")
  @classmethod
  def parse_media_json(cls, v):
    if isinstance(v, str):
      try:
        return json.loads(v)
      except json.JSONDecodeError:
        return []
    return v


class UserContentItem(ContentItem):
  rating: int
  source_url: str


class Feedback(BaseModel):
  content_id: int
  rating: int
