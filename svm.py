#!/usr/bin/env python
#coding:utf-8

class matchrow:
	def __init__(self,row,allnum=False):
		if allnum:
			self.data=[float(row[i]) for i in range(len(row)-1)]
		else:
			self.data=row[0:len(row)-1]
		self.match=int(row[len(row)-1])

def loadmatch(f,allnum=False):
	rows=[]
	with open(f) as file:
		for line in file.readlines():
			rows.append(matchrow(line.strip().split(','),allnum))
	return rows

def lineartrain(rows):
	avgs={}
	counts={}

	for row in rows:
		c1=row.match
		avgs.setdefault(c1,[0.0]*len(row.data))
		counts.setdefault(c1,0)

		for i in range(len(row.data)):
			avgs[c1][i]+=float(row.data[i])
		counts[c1]+=1
	for m,tavgs in avgs.items():
		for i in range(len(tavgs)):
			tavgs[i]/=counts[m]
	return avgs

def dotproduct(v1,v2):
	return sum(v1[i]*v2[i] for i in range(len(v1)))


#(x-(m1+m2)/2)(m1-m2) 
#x*m1-x*m2-(m1*m1-m2*m2)/2

def test(x,rows):
	avgs=lineartrain(rows)

	b=dotproduct(avgs[0],avgs[0])-dotproduct(avgs[1],avgs[1])

	a=dotproduct(x,avgs[0])-dotproduct(x,avgs[1])

	r=a-b/2
	print r
	if r>0:
		return 1
	else:
		return 0
		

if __name__=="__main__":

	rows=loadmatch('ageonly.txt',True)
	r=test([44,35],rows)

	print r
