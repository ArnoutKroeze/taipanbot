import requests
import json
import configparser as cfg
import traceback
import os
import sys

from dbhelper import DBHelper


class telegram_chatbot():

    info_text = '''Hallo daar, ik ben Daniël. Als je je punten van taipan doorgeeft in een groep of privé dan zal ik ze voor je bijhouden!
tot nu toe luister ik hier naar:

/start
Hiermee wordt de score gereset naar 0 0

/team1 <naam1> <naam2>  
Hiermee geef je aan wie er in team 1 zitten

/team2 <naam> <naam2>
idem team1

/verloop
Geeft het scoreverloop van dit spel weer'''

    
 

    def __init__(self):
        self.version = 2.4
        self.this_folder = os.path.dirname(os.path.abspath(__file__))
        self.db = DBHelper()
        with open(os.path.join(self.this_folder, 'config.json'), 'r') as file:
            data = json.load(file)
        self.token = data["TOKEN"]
        self.ADMIN = int(data["ADMIN"])
        self.URL = "https://api.telegram.org/bot{}/".format(self.token)

        self.nicknames = ('daniël', 'daniel', 'jongen', 'tyfushomo', 'daniel,', 'daniël,')
        self.compliments = ('dankje', 'lief', 'lieve', 'dank', 'braaf', 'brave', 'goed', 'goedzo', 'slim')
        self.insult = ('stomme', 'kut', 'idioot', 'stom', 'idiote', 'klote')
        self.datafile = 'testfile.json'
        self.data_file = os.path.join(self.this_folder, self.datafile)

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self, offset=None):
        url = self.URL + "getUpdates?timeout=1000"
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def get_game_id(self, user_id):
        pass

    def get_teams_from_game(self, game_id):
        pass



    def run(self):

        last_update_id = None

        while True:
            try:
                updates = self.get_updates(last_update_id)
                if "result" in updates:
                    if len(updates["result"]) > 0:
                        last_update_id = self.get_last_update_id(updates) + 1
                        self.extract_messages(updates)
            except ConnectionError as e:
                print('wajow iets ging mis dus??')
                print('')
                print(e)
                continue

    def send_message(self, text, chat_id, parse_mode=None):
        url = self.URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        if parse_mode:
            url += "&parse_mode={}".format(parse_mode)
        self.get_url(url)

    
    def extract_messages(self, updates):
        for update in updates["result"]:
            try:
                text = update["message"]["text"]
                chat = update["message"]["chat"]["id"]
                telegram_id = update["message"]["from"]["id"]
                name = update["message"]["from"]["first_name"]
                type = update["message"]["chat"]["type"]
                self.handle_message(chat, text, telegram_id, name, type)

            except Exception as e:
                print(e)
                traceback.print_stack()
                self.send_message(e, self.ADMIN)
                print("")


    def handle_message(self, chat, text, telegram_id, name, type):
        text = text.lower()
        if text[0] == "/":
            self.handle_command(chat, text, telegram_id, name)
            return

        split_text = text.split()

        for text in split_text:
            if text in self.nicknames:
                for text in split_text:
                    if text in self.insult:
                        self.send_message('nou!', chat)
                        return
                    elif text in self.compliments:
                        self.send_message(f'Dankje {name}!!!!', chat)
                        return
                    elif text == 'trein':
                        self.send_message('DE TREIN KOMT ERAAN!!!!!!!!!!!!!!!!!!!', chat)
                        return
                self.send_message('ik ben niet slim genoeg om te weten wat hier staat', chat)
                return
                
                
        if len(split_text) == 2:
            try:
                score1, score2 = int(split_text[0]), int(split_text[1])
                self.handle_score(score1, score2, chat, telegram_id)
                return
            except Exception as e:
                print(e)
                pass

        #self.send_message('Dit is geen score', chat)
    
    def handle_score(self, score1: int, score2: int, chat, telegram_id):
        if (score1 + score2) % 100:
            self.send_message('Dit is samen geen honderdtal hé', chat)
            return 
        elif score1 % 5:
            self.send_message('wtf hoe kom je aan {} punten'.format(5 - (score1 % 5)), chat)
            return
        try: 
            self.add_score(score1, score2)
            update_message = "Het staat nu {}".format(self.get_current_score())
            self.send_message(update_message, chat)
            return
        except Exception as e:
            self.send_message(e,self.ADMIN)
            self.send_message('Something went wrong', chat)
            return

    def handle_command(self, chat, text, telegram_id, name):
        switcher = {
            '/help': self.show_help,
            '/start': self.start_game,
            '/user': self.add_user,         
            '/vera': self.vera,
            '/team1': self.team_one,
            '/team2': self.team_two,
            '/verloop': self.show_scoreverloop
        }
        split_text = text.split()
        command = split_text[0].split("@")[0]
        fun = switcher.get(command, self.command_not_found)
        fun(chat, split_text, telegram_id, name)
        return

    def command_not_found(self, chat, split_text, telegram_id, name):
        self.send_message("Command not found: " + split_text[0], chat)

    def show_help(self, chat, text, telegram_id, name):
        message = "Hoiiiii {}! ik ben daniël en ik tel punten met taipan, en ik bouw kaartenhuizen van taipankaarten \nBij klachten moet je naar Jasper gaan. Hij doet informatica".format(name)
        self.send_message(message, chat)

    def start_game(self, chat, text, telegram_id, name):
        data = {
            "Team1":{
                "Player1": "null",
                "Player2": "null",
                "Scoreverloop": [0]                   
            },
            "Team2":{
                "Player1": "null",
                "Player2": "null",
                "Scoreverloop": [0]
            }
        }
        with open(self.data_file, "w") as testfile:
            json.dump(data, testfile)
        message = "We zijn een nieuw spelletje begonnen!"
        self.send_message(message, chat)
        self.db.new_game('lalala')
        return

    def team_one(self, chat, text, telegram_id, name):
        if len(text) != 3:
            self.send_message("Voer twee namen in", chat)
            return

        if len(text[1]) > 11 or len(text[2]) > 11:
            self.send_message('Max 10 letters per naam', chat)
            return

        with open(self.data_file, 'r') as file:
            print(text)
            data = json.load(file)
            print(data)



        data["Team1"]["Player1"] = text[1]
        data["Team1"]["Player2"] = text[2]

        with open(self.data_file,'w') as file:
            json.dump(data, file)
        self.send_message("ging goed", chat)
        return

    def team_two(self, chat, text, telegram_id, name):
        if len(text) != 3:
            self.send_message("Voer twee namen in", chat)
            return

        if len(text[1]) > 11 or len(text[2]) > 11:
            self.send_message('Max 10 letters per naam', chat)
            return

        with open(self.data_file, 'r') as file:
            print(text)
            data = json.load(file)
            print(data)

        print(text[1])
        data["Team2"]["Player1"] = text[1]
        data["Team2"]["Player2"] = text[2]

        with open(self.data_file,'w') as file:
            json.dump(data, file)
        self.send_message("ging goed", chat)
        return
    
    def vera(self, chat, text, telegram_id, name):
        message = "Hoi Vera, {} vindt je heel vervelend".format(name)
        self.send_message(message, chat)
        return

    def add_user(self, chat, text, telegram_id, name):
        self.send_message('uuh', chat)
        return

    def show_scoreverloop(self, chat, text, telegram_id, name):

        with open(self.data_file, 'r') as file:
            data = json.load(file)
        try:
            scores_team1 = data["Team1"]["Scoreverloop"]
            scores_team2 = data["Team2"]["Scoreverloop"]
            player1team1 = data["Team1"]["Player1"]
            player2team1 = data["Team1"]["Player2"]
            player1team2 = data["Team2"]["Player1"]
            player2team2 = data["Team2"]["Player2"]
            message = ""
            print(len(player1team1))
            # TODO make this prettier
            message += "`" + player1team1 + "".ljust(10-len(player1team1)) + player1team2 + "`\n"
            message += "`" + player2team1 + "".ljust(10-len(player2team1)) + player2team2 + "`\n"

            for line in range(len(scores_team1)):
                print('len is: {}'.format(len(str(scores_team1[line]))))
                message += "`{}".format(scores_team1[line]) + "".ljust(10-len(str(scores_team1[line]))).format(scores_team1[line]) + "{}`\n".format(scores_team2[line])
            self.send_message(message, chat, 'MarkdownV2')
            return
        except Exception as e:
            print(e)
            return

    def add_score(self, points1: int, points2: int):

        #input_scores(((self.current_game, 2, 3, points1, points2, 'probably at tuesday')))



        with open(self.data_file, "r") as testfile:
            scores = json.load(testfile)
            scores["Team1"]["Scoreverloop"] += [scores["Team1"]["Scoreverloop"][-1] + points1]
            scores["Team2"]["Scoreverloop"] += [scores["Team2"]["Scoreverloop"][-1] + points2]
        with open(self.data_file, "w") as testfile:
            json.dump(scores, testfile)
        return

    def get_current_score(self):
        with open (self.data_file, 'r') as file:
            data = json.load(file)
            punten_team1 = data["Team1"]["Scoreverloop"][-1]
            punten_team2 = data["Team2"]["Scoreverloop"][-1]
            return "{} {}".format(punten_team1, punten_team2)
        return

if __name__ == '__main__':
    daniel = telegram_chatbot()
    daniel.run()
