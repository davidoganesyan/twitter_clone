from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_path: Mapped[str] = mapped_column(String)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=True)

    tweet: Mapped["Tweet"] = relationship(  # type: ignore # noqa
        "Tweet", back_populates="media", lazy="selectin"
    )

    def __repr__(self):
        return f"<Media(id={self.id}, file_path={self.file_path})>"
