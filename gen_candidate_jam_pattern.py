# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:32:56 2017

@author: heying
"""



import pandas as pd
import datetime



def pre_handle():			#
	global dict_time_inx,dict_road_inx,link_top
	link_top=pd.read_csv('gy_contest_link_top.txt',sep=';')
	jpd = pd.read_csv('jam_data_1.5')#,nrows=50000)
	# jpd = pd.read_csv('test_r2.txt')
	# link_top=pd.read_csv('test_top.txt',sep=';')

	UniqId = list(link_top['link_ID'].astype(str))
	UniqId = sorted(set((UniqId)),key=UniqId.index)

	DateId = list(jpd['date'].astype(str))
	DateId = sorted(set((DateId)),key=DateId.index)

	road_code = [i for i in range(len(UniqId))]
	dict_road_inx = dict(zip(UniqId,road_code))
	time_code = [i for i in range(len(DateId))]
	dict_time_inx = dict(zip(DateId,time_code))

	link_top.set_index(['link_ID'],inplace=True)
	print(len(UniqId),len(DateId))
	jpd['feature_inx'] = jpd['s_time'].map(lambda x:map_time_inx(x))
	link_top['in_link_ID'] = link_top['in_links'].map(lambda x:map_in_links(x))
	jpd=jpd.drop(['Unnamed: 0','time_interval',
                 'st','in_num','out_num','length','width','link_class','travel_time',
                 's_time','v','out_links','Weekday'],axis=1)
	link_top=link_top.drop(['out_links'],axis=1)
	jpd['inx'] = jpd.apply(map_inx,axis=1)
	jpd.set_index(['inx'],inplace=True)
	return jpd


def map_time_inx(x):
    if ((x - 700)/2 > 30):
        return ((x - 700)/2 - 20)
    else:
        return (x - 700)/2
        
        
def map_in_links(x):
    sp = str(x).split('#')
    return sp


def map_inx(x):
	y = dict_time_inx[x[1]]*100000 + dict_road_inx[str(x[0])]*1000 + x[3]
	return y

    
def get_candidate_inx(x, win=9, j_inx=None):
    n_ids = link_top.ix[str(x[0])]['in_link_ID']
    candidate = [[] for i in range(5)]
    if n_ids[0] == 'nan':
        return candidate
    i = 0
    for n_id in n_ids:
        y = dict_time_inx[str(x[1])]*100000 + dict_road_inx[str(n_id)]*1000
        start = y + max(x[3]-win,0)
        end = y + min(x[3]+win,59)
        n_l = []
        for inx in range(start, end):
			if inx in j_inx:n_l.append(inx)
        # if len(n_l) >3:c+=1
        candidate[i].extend(n_l)
        i += 1
    return candidate
    

def find_jam_pattern_move_window(jam_pd,move_win=8):  
    neighbor_list = []
    # instance_list = []
    jam_inx = jam_pd.index
    inx = 0
    c = 0
    for x in xrange(len(jam_pd.index)): #row itor shouldnot sorted but jump
        row = jam_pd.iloc[x]
        candidate_inx = get_candidate_inx(row, move_win, jam_inx)
        n_l = []
        neighbor_list.append(candidate_inx)
        for i in range(len(candidate_inx)):
            if len(candidate_inx[i])>3:c+=1
    print(c)
    print(len(jam_pd))
    print(len(neighbor_list))
    jam_pd['neighbor_list'] = neighbor_list
    #jam_pd = pd.DataFrame()
    return jam_pd
    


if __name__ == '__main__':
	starttime = datetime.datetime.now()
	print starttime
	jpd = pre_handle()
	res_pd = find_jam_pattern_move_window(jam_pd=jpd)
	res_pd.to_csv('r2_8')

	endtime = datetime.datetime.now()
	print (endtime - starttime).seconds
