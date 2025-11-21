from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, select
from datetime import datetime, timezone
from .base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clients = relationship("Client", back_populates="room")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    roomId = Column(Integer, ForeignKey("rooms.id"))

    room = relationship("Room", back_populates="clients")
    messages = relationship("Message", back_populates="client", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    text = Column(String, nullable=False)
    timeStamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    message = relationship("Message", back_populates="messages")
    room = relationship("Room", back_populates="messages")
