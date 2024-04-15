from decouple import config
from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr

ENGINE = create_async_engine(config('ENGINE'))


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class User(Base):
    discord_id = Column(Integer, nullable=False)
    name = Column(String(15), nullable=True, default=None)
    birthdate = Column(Date, nullable=False)
    is_owner = Column(Boolean, default=False)


class Messages(Base):
    user = Column(ForeignKey('user.id'), nullable=False)
    user_messages = Column(Text, default='')
    ai_messages = Column(Text, default='')
    time_last_user_message = Column(DateTime, nullable=True)
