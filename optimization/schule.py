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
people=[('XU','LINYI'),
	('LIU','CHONGQING'),
	('ZHU','SHANGHAI'),
	('WANG','QINGDAO')]

destination='BEIJING'

flights={}
with open('a.txt','r') as file:
	for line in file.readlines():
		origin,dest,depart,arrive,price = line.strip().split(' ')
		flights.setdefault((origin,dest),[])
		flights[(origin,dest)].append((depart,arrive,int(price)))

#时间换算
def getminutes(t):
	x=time.strptime(t,'%H:%M')
	return x[3]*60+x[4]

#描述题解（用通用的数字序列形式来描述题）
def printschedule(r):
	for i in range(len(r)/2):
		name = people[i][0]
		origin = people[i][1]
		out = flights[(origin,destination)][r[2*i]]
		ret = flights[(destination,origin)][r[2*i+1]]
		
		print '%s %s %s %s %s %s'%(name,origin,str(out[0])+'-'+str(out[1]),out[2],str(ret[0])+'-'+str(ret[1]),ret[2])


#成本函数
def schedulecost(sol):
	out_last = 0
        ret_first = getminutes('23:59')
	#总成本
	totalprice = 0

	for i in range(len(sol)/2):
		origin = people[i][1]
		out = flights[(origin,destination)][sol[2*i]]
                ret = flights[(destination,origin)][sol[2*i+1]]
		ret_dep = getminutes(ret[0])
		out_ari = getminutes(out[1])
		#记录最早离开时间和最晚到达时间
		if out_last < out_ari:
			out_last = out_ari
		if ret_first > ret_dep:
			ret_first = ret_dep
		#往返程总票价
		totalprice += out[2]
		totalprice += ret[2]
	
	if out_last >= ret_first:
                return -1
	
	totalwait = 0
	# 每个人必须在机场等待直到最后一个人到达为止
	# 他们也必须在相同时间到达，并等候他们的返程航班
	for i in range(len(sol)/2):
		origin = people[i][1]
		out = flights[(origin,destination)][sol[2*i]]
                ret = flights[(destination,origin)][sol[2*i+1]]
		totalwait+=out_last-getminutes(out[1])
		totalwait+=getminutes(ret[0])-ret_first
		
	return totalprice+totalwait*0.5

#随机算法
def randomOptimize():
	best = 99999999
	bestr = None
	domain=[(0,5),(0,5),(0,5),(0,5),(0,5),(0,5),(0,5),(0,5)]
        for i in range(10000):
                r = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
                cost = schedulecost(r)
		if cost>0 and best > cost:
			best = cost
			bestr = r
	return bestr

#模拟退火算法
#接受高成本概率公式：p=e^(-(high-low)/T) 
#param costf 成本函数
#param T 初始温度
#param cool 冷却率
#param step 改变幅度
def simulatedAnnealing(domain,costf,T=10000,cool=0.95,step=1):
	#随机初始化一个有效值
	vec=[]
	while 1:
		vec = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
		if(schedulecost(vec)>0):
			break
	print printschedule(vec)
	print '####'

	while T>0.1:
		i = random.randint(0,len(domain)-1)
		dir = random.randint(-step,step)
		vecn = vec[:]
		vecn[i]+=dir
		if vecn[i]<domain[i][0]:vecn[i]=domain[i][0]
		elif vecn[i]>domain[i][1]:vecn[i]=domain[i][1]
		#计算当前成本和新的成本
		ca = costf(vec)
		cb = costf(vecn)
			
		if (cb>0 and cb < ca) or random.random()<pow(math.e,-(cb-ca)/T):
			vec = vecn
		#降温
		T=T*cool
	return vec

#遗传算法
#param popsize 种群大小
#param mutprob 变异概率
#param elite 被认为是优解传入下一代的概率
#param maxiter 需要传递多少代
def geneticAlgorithm(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,maxiter=100):
	#变异
	def mutate(vec):
		i = random.randint(0,len(domain)-1)
		#向上变异或向下变异的概率各占0.5
		if random.random()<0.5 and vec[i]>domain[i][0]:
			return vec[0:i]+[vec[i]-step]+vec[i+1:]
			
		elif vec[i]<domain[i][1]:
			return vec[0:i]+[vec[i]+step]+vec[i+1:]
		else:
			return vec[0:i]+[vec[i]-step]+vec[i+1:]
	#交叉
	def crossover(vec1,vec2):
		i = random.randint(1,len(domain)-2)
		return vec1[0:i]+vec[i:]

	#构造初始种群
	pop=[]
	while len(pop)<popsize:
		vec = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
		if costf(vec)>0:
			pop.append(vec)
	print pop
	#每一代中优胜劣汰后的存活精英
	topelite = int(elite*popsize)

	#开始进化100代
	for i in range(maxiter):
		#获取成本最小topN
		scores = [(costf(v),v) for v in pop]
		scores.sort()
		ranked = [v for (s,v) in scores]
		pop = ranked[0:topelite]
		#变异和交叉
		while len(pop)<popsize:
			if random.random() < mutprob:
				c = random.randint(0,topelite)
				v = mutate(ranked[c])
				if costf(v)>0:
					pop.append(v)
					
			else:
				c1 = random.randint(0,topelite)
				c2 = random.randint(0,topelite)
				v1 = crossover(ranked[c1],ranked[c2])
				if costf(v1)>0:
					pop.append(v1)
		#打印每一代的最优解
		print scores[0][0]
	
	return scores[0][1]

if __name__ == "__main__":
	domain=[(0,6),(0,6),(0,6),(0,6),(0,6),(0,6),(0,6),(0,6)]
	#best = randomOptimize()
	#best = simulatedAnnealing(domain,schedulecost)
	best = geneticAlgorithm(domain,schedulecost)
	printschedule(best)
	
