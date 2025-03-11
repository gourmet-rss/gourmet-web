from dataclasses import dataclass
from datetime import datetime
import torch


@dataclass
class Document:
  title: str
  url: str
  description: str
  date: datetime
  source_id: int
  embedding: torch.Tensor | None
