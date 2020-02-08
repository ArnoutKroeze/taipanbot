from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Games(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key = True)
    game_id = Column(Integer)
    player_1 = Column(String)
    player_2 = Column(String)
    player_3 = Column(String)
    player_4 = Column(String)
    score_1 = Column(Integer)
    score_2 = Column(Integer)
    date = Column(String)