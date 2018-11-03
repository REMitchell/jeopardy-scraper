from urllib.request import urlopen
from urllib.error import HTTPError
import html
from bs4 import BeautifulSoup
import pymysql
import requests

import re

from pymysql.err import InternalError

from answer import Answer
from question import Question
from category import Category
from database import Database
from player import Player
from score import Score
from game import Game
from html import unescape

class JeopardyScraper:
	db = None
	start = None

	def __init__(self):
		global db
		global start
		db = Database()
		start = False

	def safeGet(self, url, jsonObj=False):
		session = requests.Session()
		headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"}
		try:
			r = requests.get(url, headers=headers)
			#html = urlopen(url)
		except HTTPError as e:
			print("HTTP error "+str(e))
			return None
		except URLError as e:
			print("The server is down!")
			return None
		else:
			if r.text == None:
				print("None result at URL "+url)
				return None
			if jsonObj:
				try:
					return json.loads(r.text)
				except ValueError as e:
					print("Error parsing JSON:")
					print(r.text)
					return None
			else:
				return BeautifulSoup(r.text, "lxml")



	def formatDollars(self, stringDollars):
		dollars = re.sub("\D", "", stringDollars)
		return int(dollars)

	def byShortname(self, players, nameStr):
		for player in players:
			if player.shortname.lower() == nameStr.lower():
				return player 

	#"clue" is the beautifulsoup clue object
	#i is the round number
	def extractClue(self, clue, game, categories, i):
		global db

		clueDiv = clue.find("div")
		clueText = clue.find("td",{"class":"clue_text"}).get_text()
		
		if i == 3:
			category = categories
			order = 61
			row = 0
		else:
			coords = clue.find("td",{"class":"clue_text"}).attrs["id"].split('_')
			category = categories[int(coords[2])-1]
			row = coords[3]
			order = clueDiv.find("td", {"class":"clue_order_number"}).get_text()
		
		question = clueDiv.attrs["onmouseout"]
		answer = clueDiv.attrs["onmouseover"]
		#print("Mouseover content:")
		#print(answer)

		answer = answer[7:-1].split('\', \'')

		#Get rid of the quotes surrounding the question
		#print("Cleaned content:")
		#print(str(answer[2][:-1]))
		answerText = answer[2][:-1].replace("\\", "")
		answerObj = BeautifulSoup(str(answerText), "lxml")
		#Weird problem: Can't get an answer for these...
		if answerObj.find("em",{"class":"correct_response"}) is None:
			print("NO ANSWER FOUND!")
			return
		answerText = answerObj.find("em",{"class":"correct_response"}).get_text()
		

		notes = None
		amount = None

		if i == 3:
			#Final Jeopardy
			amount = 0

		else:
			#Find dollar values
			if clue.find("td",{"class":"clue_value_daily_double"}) != None:
				#DAILY DUBBBBLE!
				notes = "DD"
				amount = self.formatDollars(clue.find("td",{"class":"clue_value_daily_double"}).get_text())
			else:
				amount = self.formatDollars(clue.find("td",{"class":"clue_value"}).get_text())
			
		question = Question(None, game, i, category, row, order, clueText, answerText, amount, notes)
		question = question.save(db)


		#Get the answers
		if answerObj.find("td", {"class":"right"}) is not None:
			#Someone answered it right!
			name = answerObj.find("td", {"class":"right"}).get_text()
			rightPlayer = self.byShortname(game.players, name)
			answer = Answer(question, rightPlayer, "true")
			answer.save(db)

		wrongs = answerObj.findAll("td", {"class":"wrong"})
		for wrong in wrongs:
			if wrong.get_text().lower() != "triple stumper":
				#(self, id, question, player, correct)
				wrongPlayer = self.byShortname(game.players, wrong.get_text())
				answer = Answer(question, wrongPlayer, "false")
				answer.save(db)

	#Gets categories, questions and answers from the game boards
	def getQuestions(self, pageObj, game):
		global db
		rounds = pageObj.findAll("table",{"class":"round"})
		categories =[]
		if len(rounds) != 2:
			return
		for i in range(1,3):
			print("ROUND "+str(i))
			round = rounds[i-1]
			categoryElems = round.findAll("td",{"class":"category_name"})
			for category in categoryElems:
				#(self, id, game, roundNum, name):
				categoryObj = Category(None, game, i, category.get_text())
				categoryObj = categoryObj.save(db)
				categories.append(categoryObj)

			clues = round.findAll("td",{"class":"clue"})
			for clue in clues:
				if clue.find("td",{"class":"clue_text"}) is not None:
					self.extractClue(clue, game, categories, i)

		final = pageObj.find("table",{"class":"final_round"})
		if final is None:
			return
		finalCategoryName = final.find("td",{"class":"category_name"}).get_text()
		finalCategory = Category(None, game, 3, finalCategoryName)
		finalCategory = finalCategory.save(db)
		self.extractClue(final, game, finalCategory, 3) 

	def getTableScores(self, pageObj, title, coryat=False):
		regex = title+"*"

		if coryat:
			titleTag = pageObj.find("a", text="Coryat scores")
		else:
			titleTag = pageObj.find("h3", text=re.compile(title))

		if titleTag is None:
			return [None, None, None]

		if coryat:
			titleTag = titleTag.findParent("h3")

		table = titleTag.findNext("table")

		if table is None:
			return [None, None, None]

		scoresArr = []
		scoresRow = table.findAll("tr")[1]
		scores = scoresRow.findAll("td")

		for score in scores:
			score = score.get_text()
			score = score.replace("$", "")
			score = score.replace(",", "")
			scoresArr.append(int(score))

		return scoresArr



	def saveResults(self, pageObj, game, players):
		global db
		commercialBreak = self.getTableScores(pageObj, "Scores at the first commercial break")
		round1 = self.getTableScores(pageObj, "Scores at the end of the Jeopardy")
		round2 = self.getTableScores(pageObj, "Scores at the end of the Double Jeopardy")
		final = self.getTableScores(pageObj, "Final scores:")
		coryat = self.getTableScores(pageObj, "Coryat scores:", True)
		#def __init__(self, id, game, player, breakScore, round1, round2, final, coryat):
		for i in range(0,3):
			score = Score(None, game, players[i], commercialBreak[i], round1[i], round2[i], final[i], coryat[i])
			score.save(db)
		#tables = pageObj.findAll("table", attrs={})
		#tables = pageObj.findAll(lambda tag: tag.name == "table" and len(tag.attrs) == 0)


	def scrapeGame(self, url):
		global db
		global start

		if "game_id=" not in url:
			print("Invalid URL "+url)
			return
		if(url.startswith("showgame")):
			url = "http://www.j-archive.com/"+url

		skip = ["4271"]
		gameId = url.split("game_id=")[1]

		if gameId in skip:
			print("Skipping: "+str(gameId))
			return
		if gameId == "2063":
			start = True

		if not start:
			print("Skipping "+str(gameId)+"!")
			return

		bsObj = self.safeGet(url)
		#Show #153 - Wednesday, April 10, 1985
		date = bsObj.h1.get_text()
		date = date[date.index(',')+2:]
		game = Game(gameId, date)
		game.save(db)

		contestants = bsObj.findAll("p", {"class":"contestants"})
		if len(contestants) != 3:
			print("Weirdness going on with contestants in game "+str(game.id))
			return

		players = []
		for contestant in contestants:
			url = contestant.a.attrs['href']
			playerId = url.split("player_id=")[1]
			#"http://www.j-archive.com/showplayer.php?player_id=9121"
			name = contestant.a.get_text()
			description = contestant.get_text()
			description = description.replace(name, "")
			description = description[2:]
			description = description.split("(")[0]
			playerObj = Player(playerId, name, description)
			#Important to use "insert" and not append -- players are listed at the top
			#in the opposite order that the scores appear in
			players.insert(0, playerObj)

		nicknames = bsObj.findAll("td",{"class":"score_player_nickname"})
		if len(nicknames) == 0:
			print("Weirdness going on with contestant nicknames in game "+str(game.id))
			return
		#Get the first three instances of nicknames, these will be the player nicknames
		for i in range(0,3):

			players[i].setShortname(nicknames[i].get_text())
			players[i].save(db)

		game.setPlayers(players)
		self.saveResults(bsObj, game, players)
		#getQuestions(self, pageObj, game):
		self.getQuestions(bsObj, game)
		print("Done with "+str(game.id))



	def getGames(self):
		for i in range(24,33):
			html = urlopen("http://j-archive.com/showseason.php?season="+str(i))
			bsObj = BeautifulSoup(html, "lxml")
			table = bsObj.table
			games = table.findAll("")
			gameList = bsObj.find("table").findAll("a")
			for game in gameList:
				print(game['href'])
				self.scrapeGame(game['href'])


scraper = JeopardyScraper()

scraper.getGames()