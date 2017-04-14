#!/usr/bin/env python
#coding:utf-8

import sys
import datetime
import sqlite3
from math import tanh

reload(sys)
sys.setdefaultencoding('utf-8')

#param y 输出值
#return 当前输出时，tanh的斜率。
def dtanh(y):
        return 1.0-y*y

class search:
	def __init__(self,dbname):
		self.conn = sqlite3.connect(dbname)

	def __del__(self):
		self.conn.close()
	
	def dbcomit(self):
		self.conn.commit()

	def createtable(self):
		self.conn.execute('create table hiddennode (create_key)')
		self.conn.execute('create table wordhidden (fromid,toid,strength)')
		self.conn.execute('create table hiddenurl (fromid,toid,strength)')
		self.conn.commit()

	#获得连接强度
	def getStrength(self,fromid,toid,layer):
		if layer:table = 'hiddenurl'
		else: table = 'wordhidden'
		res = self.conn.execute('select strength from %s where fromid = %s and toid = %s' % (table,fromid,toid)).fetchone()
		if not res:
			#word层到hidden层的连接，默认强度为-0.2，所以在默认情况下，附加的word会对hidden的活跃程度产生负面影响。
			if layer:return 0
			else:return -0.2
		return res[0]

	#设置连接强度
	def setStrength(self,fromid,toid,layer,strength):
		if layer:table = 'hiddenurl'
                else: table = 'wordhidden'
                res = self.conn.execute('select rowid from %s where fromid = %s and toid = %s' % (table,fromid,toid)).fetchone()
		if not res:
			self.conn.execute('insert into %s (fromid,toid,strength) values (%s,%s,%s)'%(table,fromid,toid,strength))
		else:
			rowid = res[0]
			self.conn.execute('update %s set strength = %s where rowid = %s'% (table,strength,rowid))
		self.conn.commit()

	#构造与word和url相关联的隐藏节点
	def generatehiddennode(self,wordids,urlids):
		if len(wordids) > 3:return None
		create_key = '_'.join(sorted([str(wi) for wi in wordids]))
		#检查我们是否为这组单词建立好隐藏节点
		res = self.conn.execute("select rowid from hiddennode where create_key = '%s'" % create_key).fetchone()
		
		if not res:
			cur = self.conn.execute('insert into hiddennode (create_key) values ("%s")'%(create_key))
			hiddenid = cur.lastrowid

			#设置默认值
			for wordid in wordids:
				self.setStrength(wordid,hiddenid,0,1.0/len(wordids))
			for urlid in urlids:
				self.setStrength(hiddenid,urlid,1,0.1)
			self.conn.commit() 
	
	#获得所有和查询条件中的word或查询结果中的url相关联的的hiddennode
	def getAllHiddenIds(self,wordids,urlids):
		l1 = {}
		for wordid in wordids:
			cur = self.conn.execute('select toid from wordhidden where fromid = %s' % wordid)
			for row in cur:
				l1[row[0]]=1
		for urlid in urlids:
			cur = self.conn.execute('select fromid from hiddenurl where toid = %s' % urlid)
			for row in cur:
				l1[row[0]]=1
		print 'hiddenid >>> %s' % ','.join([str(i) for i in l1.keys()])
		return l1.keys()
		
	def setupnetwork(self,wordids,urlids):
		self.wordids = wordids
		self.hiddenids = self.getAllHiddenIds(wordids,urlids)
		self.urlids = urlids
		
		#节点输出
		self.ai = [1.0]*len(self.wordids)
		self.ah = [1.0]*len(self.hiddenids)
		self.ao = [1.0]*len(self.urlids)
		
		#建立权重矩阵
		self.wi = [[self.getStrength(wordid,hiddenid,0) for hiddenid in self.hiddenids] for wordid in self.wordids]
		self.wo = [[self.getStrength(hiddenid,urlid,1) for urlid in self.urlids] for hiddenid in self.hiddenids]

		print 'wi >>> %s' %','.join([str(i) for i in self.wi])
		print 'wo >>> %s' %','.join([str(i) for i in self.wo])

	#前馈法——适用S型函数tanh来计算神经元输出
	def feedforword(self):
		#查询单词是仅有的输入
		for i in range(len(self.wordids)):
			self.ai[i] = 1.0
		
		#隐藏节点的活跃程度
		for j in range(len(self.hiddenids)):
			sum = 0.0
			for i in range(len(self.wordids)):
				sum = sum + self.ai[i]*self.wi[i][j]
			print '隐藏节点活跃度 >>> %s' %str(sum)
			self.ah[j] = tanh(sum)
		
		#输出层节点的活跃程度
		for j in range(len(self.urlids)):
			sum = 0.0
			for i in range(len(self.hiddenids)):
				sum = sum + self.ah[i]*self.wo[i][j]
			print 'URL节点活跃度 >>> %s' %str(sum)
			self.ao[j] = tanh(sum)

		return self.ao[:]

	def getResult(self,wordids,urlids):
		self.setupnetwork(wordids,urlids)
		return self.feedforword()


	# param tagets 期望值(训练样本中如果是期望输出的，则为1，否则为0)
	# param N 学习速率
	def backPropagate(self,targets,N = 0.5):
		#计算输出层的误差,out_deltas为误差梯度(反向传播bp中的 -- delta rule)
		output_deltas = [0.0]*len(self.urlids)
		for k in range(len(self.urlids)):
			error = targets[k] - self.ao[k]
			output_deltas[k] = dtanh(self.ao[k])*error
		
		#计算隐藏层的误差
		hidden_deltas = [0.0]*len(self.hiddenids)
		for j in range(len(self.hiddenids)):
			error = 0.0
			for k in range(len(self.urlids)):
				error = error + output_deltas[k]*self.wo[j][k]
			hidden_deltas[j] = dtanh(self.ah[j])*error

		#更新输出权重
		for j in range(len(self.hiddenids)):
			for k in range(len(self.urlids)):
				change = output_deltas[k]*self.ah[j]
				self.wo[j][k] = change*N + self.wo[j][k]

		#更新输入权重
		for i in range(len(self.wordids)):
			for j in range(len(self.hiddenids)):
				change = hidden_deltas[j]*self.ai[i]
				self.wi[i][j] = change*N + self.wi[i][j] 
	
	#训练试验
	#param selectedurl 期望输出结果
	def trainQuery(self,wordids,urlids,selectedurl):
		#生成隐藏节点
		self.generatehiddennode(wordids,urlids)
		#构建网络——获取每个节点上的活跃度，以及节点间连接的权重值。
		self.setupnetwork(wordids,urlids)			
		self.feedforword()
		targets = [0.0]*len(urlids)
		targets[urlids.index(selectedurl)]=1.0
		#利用反向传播更新连接权重
		self.backPropagate(targets)
		self.updatedatabase()
	
	#更新数据库中的连接权重值
	def updatedatabase(self):
		for i in range(len(self.wordids)):
			for j in range(len(self.hiddenids)):
				self.setStrength(self.wordids[i],self.hiddenids[j],0,self.wi[i][j])
		for j in range(len(self.hiddenids)):
			for k in range(len(self.urlids)):
				self.setStrength(self.hiddenids[j],self.urlids[k],1,self.wo[j][k])
		self.conn.commit()

	

if __name__ == "__main__":
	s = search('test.db')
	wPython,wCold,wSocket = 101,102,103
	uTcp,uAnimal,uJava = 201,202,203
	
	
	allurlids = [uTcp,uAnimal,uJava]
	'''	
	#样本训练
	for i in range(30):
		s.trainQuery([wPython,wSocket],allurlids,uTcp)
       		s.trainQuery([wPython,wCold],allurlids,uAnimal)
		s.trainQuery([wPython],allurlids,uJava)
		s.trainQuery([wSocket],allurlids,uTcp)
	#s.generatehiddennode([wWorld,wBank],allurlids)
	'''
	#cur = conn.execute('delete from hiddenurl')
	#s.conn.commit()
	
	#sys.exit(0)


	cur = s.conn.execute('select * from wordhidden')
	print 'wordhidden'
	for i in cur:
		print i

	cur = s.conn.execute('select * from hiddenurl')
        print 'word'
        for i in cur:
                print i

	cur = s.conn.execute('select * from hiddennode')
        print 'hiddenode'
        for i in cur:
                print i

	print 'result >> ',s.getResult([wCold],allurlids)
