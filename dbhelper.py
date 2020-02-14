from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from base import Base, Games, Admins


class DBHelper:
    session = None
    engine = None

    def __init__(self, dbname="taipan.sqlite"):
        self.engine = create_engine('sqlite:///' + dbname, echo=False)
        sessionFactory = sessionmaker(bind=self.engine)
        self.session = sessionFactory()
        Base.metadata.create_all(self.engine)

    def get_max_game_id(self):
        try:
            max_id = self.session.query(func.max(Games.game_id)).first()[0]
            max_id = int(max_id)
        except Exception:
            max_id = 0

        if type(max_id) != int:
            max_id = 0
        return max_id


    def new_game(self, player_1, player_2, player_3, player_4, date):
        game_id = self.get_max_game_id() + 1
        game = Games(game_id = game_id, player_1 = player_1, player_2 =  player_2, player_3 = player_3, player_4 =  player_4, score_1 = 0,score_2 = 0, date = date)
        self.session.add(game)
        self.session.commit()
        return

    def add_score(self, score1, score2, date):
        scores = self.session.query(Games).filter_by(game_id = self.get_max_game_id()).first()
        new_scores = Games(game_id = scores.game_id, player_1 = scores.player_1, player_2 = scores.player_2,
                    player_3 = scores.player_3, player_4 = scores.player_4, score_1 = score1, score_2 = score2,
                    date = date)
        self.session.add(new_scores)
        self.session.commit()
        return
    
    def current_score(self):
        games = self.session.query(Games).filter_by(game_id = self.get_max_game_id())
        total_1 = 0
        total_2 = 0
        for game in games:
            total_1 += game.score_1
            total_2 += game.score_2
        return f"{total_1}, {total_2}"

    def scoreverloop(self):
        games = (self.session.query(Games)
                .filter_by(game_id = self.get_max_game_id())
                .order_by(Games.date))

        verloop = ""
        verloop += "`" + games[0].player_1 + "".ljust(10-len(games[0].player_1)) + games[0].player_3 + "`\n"
        verloop += "`" + games[0].player_2 + "".ljust(10-len(games[0].player_2)) + games[0].player_4 + "`\n"

        team1 = 0
        team2 = 0
        for game in games:
            team1 += game.score_1
            team2 += game.score_2
            verloop += f"`{team1}" + "".ljust(10 - len(str(team1))) + f"{team2}`\n"
        return verloop
        

    def add_admin(self, admin_id, name):
        admin = Admins(admin_id = admin_id, name = name)
        self.session.add(admin)
        self.session.commit()
        return

    def check_admin(self, admin_id):
        #check by id
        print()
        user = self.session.query(Admins).filter_by(admin_id = admin_id).first()
        if user:
            if user.admin_id == admin_id:
                return True
            else:
                return False
        else:
            return False

if __name__ == "__main__":
    db = DBHelper()

