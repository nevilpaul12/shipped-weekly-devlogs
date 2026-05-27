from pydantic import BaseModel
from datetime import datetime


class DevLogs(BaseModel):
    title: str
    description: str
    links: list[str] | None = None
    images: list[str] | None = None
    takeaway: str

