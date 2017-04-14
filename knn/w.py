class W:
	def __enter__(self):
		print 'enter'
		print 1/0
		return self

	def __exit__(self,a,b,c):
		print 'exit'
		print 'a>>> %s'% a
		print 'b>>> %s'% b
		print 'c>>> %s'% c

	def f(self):
		print 123
		print 1/0


if __name__ == '__main__':
	with W() as w:
		w.f()
	
