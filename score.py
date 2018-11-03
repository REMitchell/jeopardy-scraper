from pymysql.err import InternalError
from database import Database

class Score:

	def __init__(self, id, game, player, breakScore, round1, round2, final, coryat):
		self.id = id
		self.game = game
		self.player = player
		self.breakScore = breakScore
		self.round1 = round1
		self.round2 = round2
		self.final = final
		self.coryat = coryat

	def save(self, db):

		try:
			db.cur.execute("SELECT * FROM scores WHERE playerId = %s AND gameId = %s", (int(self.player.id), int(self.game.id)))

			if db.cur.rowcount == 0:
				db.cur.execute("INSERT INTO scores (gameId, playerId, breakScore, round1, round2, final, coryat) VALUES (%s, %s, %s, %s, %s, %s, %s)", (int(self.game.id), int(self.player.id), self.breakScore, self.round1, self.round2, self.final, self.coryat))
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
