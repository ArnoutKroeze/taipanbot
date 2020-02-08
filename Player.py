from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from base import Base

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    current_game = Column(Integer)


    def __init__(self, name):
        self.name = name
        self.current_game = 0

    