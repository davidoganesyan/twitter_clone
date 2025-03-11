from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    api_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)

    tweets: Mapped[list["Tweet"]] = relationship(  # type: ignore # noqa
        "Tweet", back_populates="author", lazy="selectin", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(  # type: ignore # noqa
        "Like", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    following: Mapped[list["User"]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.id == Follower.follower_id",
        secondaryjoin="User.id == Follower.followed_id",
        back_populates="followers",
        lazy="selectin",
    )
    followers: Mapped[list["User"]] = relationship(
        "User",
        secondary="followers",
        primaryjoin="User.id == Follower.followed_id",
        secondaryjoin="User.id == Follower.follower_id",
        back_populates="following",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"
