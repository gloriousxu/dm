#!/usr/bin/env python
#coding:utf-8

import sys
import random
import math
import re

reload(sys)
sys.setdefaultencoding('utf-8')

def s():
	print 'sss'

class c():
	b=2
	def __init__(self):
		self.a=1
		print 'c is init ...'

	def f(self):
		print 'f is running'

	def f1(self,a):
		print 'f1 sss'+str(a)

class cc(c):

	def __init__(self):
		print 'cc is ini...'	
	def f(self):
		print ' cc .f is running'
