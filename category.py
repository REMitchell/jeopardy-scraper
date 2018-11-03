from pymysql.err import InternalError
from database import Database

class Category:

	def __init__(self, id, game, roundNum, name):
		self.id = id
		self.game = game
		self.round = roundNum
		self.name = name

	def save(self, db):
		try:
			db.cur.execute("SELECT * FROM categories WHERE name = %s AND gameId = %s AND round = %s", (self.name, int(self.game.id), int(self.round)))
			if db.cur.rowcount == 0:
				db.cur.execute("INSERT INTO categories (gameId, round, name) VALUES (%s, %s, %s)", (int(self.game.id), int(self.round), self.name))
				db.conn.commit()
				self.id = db.cur.lastrowid
			else:
				self.id = db.cur.fetchall()[0]["id"]
				
		except InternalError as e:
			print("Internal error!")
			print(e)
			db.conn.rollback()
		except:
			print("Mystery error!")
			print(e)
			db.conn.rollback()
			
		return self
