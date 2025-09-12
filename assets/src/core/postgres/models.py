from sqlalchemy import UUID, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from src.core.postgres.base import BaseModel


class User(BaseModel):
    __tablename__: str = "users"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(255), unique=False, index=False, nullable=False
    )
