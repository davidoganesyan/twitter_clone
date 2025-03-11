from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"))

    user: Mapped["User"] = relationship(  # type: ignore # noqa
        "User", back_populates="likes", lazy="selectin"
    )
    tweet: Mapped["Tweet"] = relationship(  # type: ignore # noqa
        "Tweet", back_populates="likes", lazy="selectin"
    )

    def __repr__(self):
        return f"<Like(user_id={self.user_id}, tweet_id={self.tweet_id})>"
