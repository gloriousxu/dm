#!/usr/bin/env python
#coding:utf-8

import sys
import time
import sqlite3
import random
import math

reload(sys)
sys.setdefaultencoding('utf-8')

#初始化数据
dorms=('DAWEICHENG','YINGGUOGONG','DAHU','JIANQIAOJUN')

people=[('XU',('DAWEICHENG','DAHU')),
	('HE',('JIANQIAOJUN','DAHU')),
	('HAN',('DAWEICHENG','JIANQIAOJUN')),
	('ZHANG',('YINGGUOGONG','DAHU')),
	('GUO',('DAWEICHENG','YINGGUOGONG')),
	('LIU',('DAHU','DAWEICHENG')),
	('SUN',('YINGGUOGONG','DAHU')),
	('TAN',('DAWEICHENG','YINGGUOGONG'))]


#描述题解（用通用的数字序列形式来描述题）
def printsolution(r):
	slots=[]
	for i in range(len(dorms)):
		slots+=[i,i]
		
	for i in range(len(r)):
		name = people[i][0]
		dorm = dorms[slots[r[i]]]
		print 'name >>> %s dorm >>> %s'%(name,dorm)
		
		del slots[r[i]]

#成本函数
def solutioncost(sol):
	slots=[]
	cost = 0
	for i in range(len(dorms)):
		slots+=[i,i]
	for i in range(len(sol)):
		x=sol[i]
		dorm = dorms[slots[x]]
		pref=people[i][1]
		if pref[0] == dorm:
			cost+=0
		elif pref[1] == dorm:
			cost+=1
		else:
			cost+=3 
	return cost

if __name__ == "__main__":
	domain=[(0,len(dorms)*2-1-i) for i in range(len(dorms)*2)]
	print domain
	
	#best = randomOptimize()
	#best = simulatedAnnealing(domain,schedulecost)
	vec = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
	print vec
	printsolution(vec)
	print solutioncost(vec)

