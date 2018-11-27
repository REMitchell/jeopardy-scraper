from pymysql.err import InternalError
from database import Database

class Game:

	def __init__(self, id, date):
		self.id = id
		self.date = date
		self.players = None
		self.categories = None

	def setCategories(self, categories):
		self.categories = categories

	def setPlayers(self, players):
		self.players = players

	def save(self, db):
		try:
			db.cur.execute("SELECT * FROM games WHERE id = %s", (int(self.id)))
			if db.cur.rowcount == 0:
				db.cur.execute("INSERT INTO games (id, date) VALUES (%s, %s)", (int(self.id), self.date))
				db.conn.commit()
				
		except InternalError as e:
			print("Internal error!")
			print(e)
			db.conn.rollback()
		except e:
			print("Mystery error!")
			print(e)
			db.conn.rollback()
		return self