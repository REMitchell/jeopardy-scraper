from pymysql.err import InternalError
from database import Database

class Question:

	def __init__(self, id, game, roundNum, category, row, order, clue, answer, amount, notes=None):
		self.id = id
		self.game = game
		self.round = roundNum
		self.row = row
		self.category = category
		self.order = order
		self.clue = clue
		self.answer = answer
		self.amount = amount
		#IF the question is a daily double, this will be "DD"
		self.notes = notes

	def save(self, db):
		try:
			db.cur.execute("SELECT * FROM questions WHERE gameId = %s AND round = %s AND categoryId=%s AND row=%s", (int(self.game.id), int(self.round), int(self.category.id), int(self.row)))
			if db.cur.rowcount == 0:
				db.cur.execute("INSERT INTO questions (gameId, round, row, categoryId, pickorder, clue, answer, amount, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (int(self.game.id), int(self.round), int(self.row), int(self.category.id), int(self.order), self.clue, self.answer, int(self.amount), self.notes))                                                               
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
			db.conn.rollback()
		return self


