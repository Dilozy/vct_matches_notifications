from sqlalchemy import select, delete, exists

from .database import session_factory
from .models import SubscribersORM, TeamsORM, Subscriptions, RegionsORM


class Repository:
    @staticmethod
    def select_not_subscribed_teams(user_chat_id, region):
        with session_factory() as session:
            subq = (
                select(TeamsORM.name)
                .join(Subscriptions, Subscriptions.team_name==TeamsORM.name)
                .join(SubscribersORM, SubscribersORM.id==Subscriptions.subscriber_id)
                .where(SubscribersORM.id==user_chat_id)
                .scalar_subquery()
                )
            
            available_teams_query = (
                select(TeamsORM.name)
                .where(TeamsORM.region_name==region)
                .where(~TeamsORM.name.in_(subq))
            )

            result = session.execute(available_teams_query).scalars().all()
            
            return result
            
    @staticmethod
    def add_subscription(user_chat_id, team_name):
        with session_factory() as session:
            subscriber = session.get(SubscribersORM, user_chat_id)
            
            team = session.query(TeamsORM).filter(TeamsORM.name==team_name).first()

            if team not in subscriber.subscribed_to:
                subscriber.subscribed_to.append(team)
            
            session.commit()

    @staticmethod
    def list_user_subscriptions(user_chat_id):
        with session_factory() as session:
            query = (
                select(TeamsORM.name, RegionsORM.name)
                .join(Subscriptions, TeamsORM.name==Subscriptions.team_name)
                .join(SubscribersORM, SubscribersORM.id==Subscriptions.subscriber_id)
                .join(RegionsORM, TeamsORM.region_name==RegionsORM.name)
                .filter(SubscribersORM.id==user_chat_id)
                )

            return dict(session.execute(query).all())
        
    @staticmethod
    def remove_subscription(user_chat_id, team):
        with session_factory() as session:
            delete_query = (
                delete(Subscriptions)
                .where(Subscriptions.subscriber_id==user_chat_id)
                .where(Subscriptions.team_name==team)
            )

            session.execute(delete_query)
            session.commit()

    @staticmethod
    def list_all_teams():
        with session_factory() as session:
            return session.query(TeamsORM.name).scalars().all()
        
    @staticmethod
    def check_user(user_chat_id):
        with session_factory() as session:
            stmt = select(exists().where(SubscribersORM.id == user_chat_id))
            return session.execute(stmt).scalar()

    @staticmethod
    def create_subscriber(user_chat_id, timezone):
        with session_factory() as session:
            user = SubscribersORM(id=user_chat_id, timezone=timezone)
            session.add(user)

            session.commit()

    @staticmethod
    def list_subscribed_users(team_name):
        with session_factory() as session:
            stmt = (
                select(SubscribersORM.id)
                .join(SubscribersORM.id == Subscriptions.subscriber_id)
                .join(TeamsORM.name == Subscriptions.team_name)
                .where(TeamsORM.name == team_name)
            )

            return session.execute(stmt).scalars().all()