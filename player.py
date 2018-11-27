from pymysql.err import InternalError
from database import Database

class Player:

	def __init__(self, id, name, background, shortname=None):
		self.id = id
		self.name = name
		self.shortname = shortname
		self.background = background

	def setShortname(self, shortname):
		self.shortname = shortname

	def save(self, db):
		print("PLAYER: "+self.name+" -- "+self.shortname)
		try:
			db.cur.execute("SELECT * FROM players WHERE id="+str(self.id))
			if db.cur.rowcount == 0:
				db.cur.execute("INSERT INTO players (id, name, shortname, background) VALUES (%s, %s, %s, %s)", (int(self.id), self.name, self.shortname, self.background))
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