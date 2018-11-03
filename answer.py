from database import Database
from pymysql.err import InternalError

class Answer:
	
	def __init__(self, question, player, correct):
		self.question = question
		self.player = player
		self.correct = correct

	def save(self, db):

		try:
			db.cur.execute("SELECT * FROM answers WHERE questionId = %s AND playerId = %s", (int(self.question.id), int(self.player.id)))

			if db.cur.rowcount == 0:
				print("INSERT INTO answers (questionId, playerId, correct) VALUES ("+str(self.question.id)+", "+str(self.player.id)+", "+str(self.correct)+")")
				db.cur.execute("INSERT INTO answers (questionId, playerId, correct) VALUES (%s, %s, %s)", (int(self.question.id), int(self.player.id), self.correct))
				db.conn.commit()
				self.id = db.cur.lastrowid
			else:
				self.id = db.cur.fetchall()[0]["id"]

		except InternalError as e:
			print("INSERT INTO answers (questionId, playerId, correct) VALUES ("+str(self.question.id)+", "+str(self.player.id)+", "+str(self.correct)+")")

			print("Internal error!")
			print(e)
			db.conn.rollback()


		return self

