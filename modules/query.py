import numpy as np

def query_data(map, self, heros, fruits, bombs, fire, act):
	n=map.height
	m=map.width
	k=1+2+2+5+1
	data_dict={}
	pos=np.zeros((k, n, m))
	# 地图层
	for i in range(n):
		for j in range(m):
			if map.instances_list[i][j] not in '012':
				pos[0,i,j]=1
	# 英雄层
	# 自己
	pos[1+0,self.coordinate[1],self.coordinate[0]]=1
	data_dict['Hero']=self.health_value
	data_dict['action']=act
	# 敌人
	i=0
	for hero in heros:
		pos[1+1,hero.coordinate[1],hero.coordinate[0]]=1
		data_dict['Enemy'+str(i)]=hero.health_value
		i+=1
	# 水果层
	for fruit in fruits:
		if fruit.value == 5:
			pos[1+2+0,fruit.coordinate[1],fruit.coordinate[0]]=1
		elif fruit.value == 10:
			pos[1+2+1,fruit.coordinate[1],fruit.coordinate[0]]=1
	# 炸弹层
	for bomb in bombs:
		if bomb.explode_millisecond >= 4000:
			pos[1+2+2+4,bomb.coordinate[1],bomb.coordinate[0]]=1
		elif bomb.explode_millisecond >= 3000:
			pos[1+2+2+3,bomb.coordinate[1],bomb.coordinate[0]]=1
		elif bomb.explode_millisecond >= 2000:
			pos[1+2+2+2,bomb.coordinate[1],bomb.coordinate[0]]=1
		elif bomb.explode_millisecond >= 1000:
			pos[1+2+2+1,bomb.coordinate[1],bomb.coordinate[0]]=1
		elif bomb.explode_millisecond > 0:
			pos[1+2+2+0,bomb.coordinate[1],bomb.coordinate[0]]=1
	# 火焰层
	for f in fire:
		pos[1+2+2+5,f[1],f[0]]=1
	
	data_dict['state']=pos
	return data_dict