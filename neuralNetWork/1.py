#generate Tree

arr = [[1,0],[2,1],[6,1],[3,2],[4,2],[5,2],[7,6],[8,6]]

p=[{1:[]}]
def fun(p):
	for i in p:
		k=i.items()[0][0]
		v=i.items()[0][1]
		
		for j in arr:
			if j[1]==k:
				d={}
				d[j[0]]=[]
				if j[0] not in set([i.items()[0][0] for i in v]):
					v.append(d)
					fun(v)
	return p
	
print fun(p)

	 
