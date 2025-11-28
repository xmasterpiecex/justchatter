from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from .base import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String, unique=True, nullable=False)

    clients = relationship("Client", back_populates="room")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_name = Column(String, unique=True, nullable=False)
    client_cache_num = Column(Integer, unique=True, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    room = relationship("Room", back_populates="clients")
    messages = relationship("Message", back_populates="client", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    timeStamp = Column(String, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    client = relationship("Client", back_populates="messages")
    room = relationship("Room", back_populates="messages")
