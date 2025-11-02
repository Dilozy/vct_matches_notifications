from sqlalchemy import select, delete, exists

from src.repository.database import session_factory
from src.repository.models import SubscribersORM, TeamsORM, Subscriptions, RegionsORM


class Repository:
    @staticmethod
    def select_not_subscribed_teams(user_chat_id: int, region: str) -> list[str]:
        with session_factory() as session:
            subq = (
                select(Subscriptions.team_name)
                .where(Subscriptions.subscriber_id == user_chat_id)
                .scalar_subquery()
                )
            
            available_teams_query = (
                select(TeamsORM.name)
                .where(TeamsORM.region_name == region)
                .where(~TeamsORM.name.in_(subq))
                .order_by(TeamsORM.name.asc())
            )

            result = session.execute(available_teams_query).scalars().all()
            
            return result
            
    @staticmethod
    def add_subscription(user_chat_id: int, team_name: str) -> None:
        with session_factory() as session:
            subscriber = session.get(SubscribersORM, user_chat_id)
            
            team = session.query(TeamsORM).filter(TeamsORM.name==team_name).first()

            if team not in subscriber.subscribed_to:
                subscriber.subscribed_to.append(team)
            
            session.commit()

    @staticmethod
    def list_user_subscriptions(user_chat_id: int) -> dict[str, str]:
        with session_factory() as session:
            query = (
                select(TeamsORM.name, RegionsORM.name)
                .join(TeamsORM.subscribers)
                .join(TeamsORM.region)
                .filter(SubscribersORM.id == user_chat_id)
            )

            return dict(session.execute(query).all())
        
    @staticmethod
    def remove_subscription(user_chat_id: int, team: str) -> None:
        with session_factory() as session:
            delete_query = (
                delete(Subscriptions)
                .where(Subscriptions.subscriber_id == user_chat_id)
                .where(Subscriptions.team_name == team)
            )

            session.execute(delete_query)
            session.commit()

    @staticmethod
    def list_all_teams() -> list[str]:
        with session_factory() as session:
            stmt = select(TeamsORM.name)
            return session.execute(stmt).scalars().all()
        
    @staticmethod
    def check_user(user_chat_id: int) -> bool:
        with session_factory() as session:
            stmt = select(exists().where(SubscribersORM.id == user_chat_id))
            return session.execute(stmt).scalar()

    @staticmethod
    def create_subscriber(user_chat_id: int) -> SubscribersORM:
        with session_factory() as session:
            user = SubscribersORM(id=user_chat_id)
            session.add(user)

            session.commit()
            return user

    @staticmethod
    def list_subscribed_users(team_names: list[str]) -> list[int]:
        with session_factory() as session:
            stmt = (
                select(SubscribersORM.id)
                .join(SubscribersORM.subscribed_to)
                .where(TeamsORM.name.in_(team_names))
            )
            return session.execute(stmt).scalars().all()
