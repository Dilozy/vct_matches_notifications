from sqlalchemy import select, delete, exists

from src.db.connect import session_factory
from src.db.models import Subscriber, Team, Subscription, Region


class TeamRepository:
    @staticmethod
    def select_not_subscribed_teams(user_chat_id: int, region: str) -> list[str]:
        with session_factory() as session:
            subq = (
                select(Subscription.team_name)
                .where(Subscription.subscriber_id == user_chat_id)
                .scalar_subquery()
                )
            
            available_teams_query = (
                select(Team.name)
                .where(Team.region_name == region)
                .where(~Team.name.in_(subq))
                .order_by(Team.name.asc())
            )

            result = session.execute(available_teams_query).scalars().all()
            
            return result

    @staticmethod
    def list_teams() -> list[str]:
        with session_factory() as session:
            stmt = select(Team.name)
            return session.execute(stmt).scalars().all()
        
    @staticmethod
    def list_subscribers(team_names: list[str]) -> list[int]:
        with session_factory() as session:
            stmt = (
                select(Subscriber.id)
                .join(Subscriber.subscribed_to)
                .where(Team.name.in_(team_names))
                .distinct()
            )
            return session.execute(stmt).scalars().all()


class SubscriberRepository:
    @staticmethod
    def check_subscriber(user_chat_id: int) -> bool:
        with session_factory() as session:
            stmt = select(exists().where(Subscriber.id == user_chat_id))
            return session.execute(stmt).scalar()

    @staticmethod
    def create_subscriber(user_chat_id: int) -> Subscriber:
        with session_factory() as session:
            user = Subscriber(id=user_chat_id)
            session.add(user)

            session.commit()
            return user


class SubscriptionRepository:
    @staticmethod
    def add_subscription(user_chat_id: int, team_name: str) -> None:
        with session_factory() as session:
            subscriber = session.get(Subscriber, user_chat_id)
            
            team = session.query(Team).filter(Team.name==team_name).first()

            if team not in subscriber.subscribed_to:
                subscriber.subscribed_to.append(team)
            
            session.commit()

    @staticmethod
    def list_subscriptions(user_chat_id: int) -> dict[str, str]:
        with session_factory() as session:
            query = (
                select(Team.name, Region.name)
                .join(Team.subscribers)
                .join(Team.region)
                .filter(Subscriber.id == user_chat_id)
            )

            return dict(session.execute(query).all())
        
    @staticmethod
    def remove_subscription(user_chat_id: int, team: str) -> None:
        with session_factory() as session:
            delete_query = (
                delete(Subscription)
                .where(Subscription.subscriber_id == user_chat_id)
                .where(Subscription.team_name == team)
            )

            session.execute(delete_query)
            session.commit()
