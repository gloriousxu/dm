#!/usr/bin/env python
#coding:utf-8

import sys
import random
import math
import re

reload(sys)
sys.setdefaultencoding('utf-8')

def getwords(doc):
	splitter=re.compile('\\W*')
	words = [word.lower() for word in splitter.split(doc.strip()) if len(word)>2 and len(word)<20]
	return dict([(w,1) for w in words])

class classifier():
	def __init__(self,getfeatures,filename = None):
		#统计特征/分类组合数量
		self.fc={}
		#统计每个分类中文档的数量
		self.cc={}
		#获取特征方法（getwords()）
		self.getfeatures = getfeatures
	
	def incf(self,f,cat):
		self.fc.setdefault(f,{})
		self.fc[f].setdefault(cat,0.0)
		self.fc[f][cat]+=1

	def incc(self,cat):
		self.cc.setdefault(cat,0.0)
		self.cc[cat]+=1

	def fcount(self,f,cat):
		if f in self.fc and cat in self.fc[f]:
			return self.fc[f][cat]
		return 0.0
	
	def ccount(self,cat):
		if cat in self.cc:
			return self.cc[cat]
		return 0.0

	def totalcount(self):
		return sum(self.cc.values())
	
	def categories(self):
		return self.cc.keys()
		
	def train(self,item,cat):
		features = self.getfeatures(item)
		for i in features:
			self.incf(i,cat)
		self.incc(cat)

	def fprob(self,f,cat):
		if self.ccount(cat)==0:return 0
		return self.fcount(f,cat)/self.ccount(cat)

	def weightfprob(self,f,cat,weight=1.0,assumeprob=0.5):
		prob=self.fprob(f,cat)
		total=sum([self.fcount(f,c) for c in self.categories()])
		return (weight*assumeprob+total*prob)/(weight+total)

#朴素贝叶斯分类器	
class naivebayesclassifier(classifier):
	def __init__(self,getfeatures):
		classifier.__init__(self,getfeatures)
		self.threshold={}
	
	def docprob(self,item,cat):
		fs = self.getfeatures(item)
		p=1
		for f in fs:
			p*=self.weightfprob(f,cat)
		return p

	def bayesprob(self,item,cat):
		catprob=self.ccount(cat)/self.totalcount()
		docprob=self.docprob(item,cat)
		return catprob*docprob

	def setthreshold(self,cat,t):
		self.threshold[cat]=t

	def getthreshold(self,cat):
		return self.threshold[cat]

	def bayesclassifer(self,item,default=None):
		ic={}
		max=0
		for c in self.categories():
			p=self.bayesprob(item,c)
			ic[c]=p
			if p>max:
				max=p
				best=c

		print ic		

		for cp in ic:
			if cp == best:continue
			threshold = self.getthreshold(best)
			if ic[cp]*threshold>ic[best]:
				return default
			return best

				
def sampletrain(c):
	c.train('nobodys own the water.','good')
	c.train('the quick rabbit jumps fences.','good')
	c.train('buy pharmacheutials now !','bad')
	c.train('make quick money at the online casino!','bad')
	c.train('the quick brown fox jumps','good')


if __name__ == '__main__':
	#c=classifier(getwords)
	#sampletrain(c)
	bayes = naivebayesclassifier(getwords)
	sampletrain(bayes)
	bayes.setthreshold('good',1)
	bayes.setthreshold('bad',3)
	cat=bayes.bayesclassifer('quick rabbit','unknown')	
	print cat


