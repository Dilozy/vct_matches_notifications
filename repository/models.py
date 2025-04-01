from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class SubscribersORM(Base):
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    subscribed_to: Mapped[list["TeamsORM"]] = relationship(
        back_populates="subscribers",
        secondary="subscriptions",
    )


class TeamsORM(Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(primary_key=True)
    region_name: Mapped[int] = mapped_column(ForeignKey("regions.name", ondelete="CASCADE"))
    region: Mapped["RegionsORM"] = relationship(
        back_populates="teams",
    )
    subscribers: Mapped[list["SubscribersORM"]] = relationship(
        back_populates="subscribed_to",
        secondary="subscriptions"
    )

    def __repr__(self):
        return f"TeamsORM(name={self.name})"

class RegionsORM(Base):
    __tablename__ = "regions"

    name: Mapped[str] = mapped_column(primary_key=True)
    teams: Mapped[list["TeamsORM"]] = relationship(
        back_populates="region",
        cascade="all, delete-orphan",
    )

class Subscriptions(Base):
    __tablename__ = "subscriptions"

    team_name: Mapped[str] = mapped_column(ForeignKey("teams.name", ondelete="CASCADE"),
                                         primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("subscribers.id"), primary_key=True)
