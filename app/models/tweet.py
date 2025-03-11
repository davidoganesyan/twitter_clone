from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author: Mapped["User"] = relationship(  # type: ignore # noqa
        "User", back_populates="tweets", lazy="selectin"
    )
    media: Mapped[list["Media"]] = relationship(  # type: ignore # noqa
        "Media", back_populates="tweet", lazy="selectin", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(  # type: ignore # noqa
        "Like", back_populates="tweet", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tweet(id={self.id}, author_id={self.author_id})>"
