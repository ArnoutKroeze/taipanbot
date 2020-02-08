from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from base import Base, Games


class DBHelper:
    session = None
    engine = None

    def __init__(self, dbname="taipan.sqlite"):
        self.engine = create_engine('sqlite:///' + dbname, echo=False)
        sessionFactory = sessionmaker(bind=self.engine)
        self.session = sessionFactory()
        Base.metadata.create_all(self.engine)

    def get_max_game_id(self):
        print(self.session.querry(func.max(games.game_id)).first())
        pass


    def new_game(self, date):
        game = Games(game_id = 2, player_1 = 'arnout',player_2 =  'Japser',player_3 = 'anna',player_4 =  'Peter', score_1 = 0,score_2 = 0, date = date)
        self.session.add(game)
        self.session.commit()

    def add_score(self, score1, score2):
        pass
    
db = DBHelper()
if __name__ == "__main__":
    db.new_game('bier')
    db.get_max_game_id()
    
    print('taipan!')
