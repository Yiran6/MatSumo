# Program to run the Seattle downtown network
import numpy as np
import os
import traci
import sys
import optparse
from sumolib import checkBinary
from numpy import genfromtxt
from data_extract import get_data

def convert_od_file(od_csv, od_txt, taz_add_file, route_file, ped=True):
	print('Generate the OD.txt file')
	OD_data = genfromtxt(od_csv, delimiter=',')
	row, colume = np.shape(OD_data)
	with open(od_txt,"w") as OD:
		OD.write("$OR;\n")
		OD.write("*From time, TO time\n")
		OD.write("0.00 24.00\n")
		OD.write("*Factor\n")
		OD.write("1\n")
		for i in range(1,row):
			OD.write("%i %i %i\n" %(OD_data[i,0], OD_data[i,1], OD_data[i,2]))
		OD.close()

	print('Generate the OD.rou.xml file')
	#os.system('od2trips -n Seattle_taz.add.xml -d Seattle_OD.txt -o Seattle_rou.xml')

	# os.system('od2trips -n Seattle_taz.add.xml -d Seattle_OD.txt --timeline.day-in-hours -o Seattle_rou.xml')

	# os.system('od2trips -n Seattle_taz.add.xml -d Seattle_OD.txt -o Seattle_rou.xml --timeline.day-in-hours \
	# --timeline 0.2,0.2,0.2,0.2,0.3,0.4,0.6,0.8,1.0,0.8,0.6,0.5,0.5,0.5,0.5,0.6,0.8,1.0,0.8,0.6,0.4,0.3,0.2,0.2')
	#os.system('od2trips -n Seattle_taz.add.xml -d Seattle_OD.txt -o Seattle_rou.xml --timeline.day-in-hours \
	# --timeline 0.0,0.0,0.0,0.0,0.1,0.3,0.6,0.8,1.0,0.8,0.6,0.5,0.5,0.5,0.5,0.6,0.8,1.0,0.8,0.6,0.4,0.2,0.1,0.1')
	
	if ped == True:
		query = 'od2trips -n '+taz_add_file+' -d '+od_txt+' -o '+route_file+' --pedestrians --timeline.day-in-hours \
		--timeline 0.0,0.0,0.0,0.0,0.1,0.1,0.1,0.9,1.0,0.9,0.3,0.3,0.5,0.5,0.3,0.3,0.9,1.0,0.9,0.6,0.2,0.1,0.1,0.1'
	else:
	#  os.system(query)
		query = 'od2trips -n '+taz_add_file+' -d '+od_txt+' -o '+route_file+' --timeline.day-in-hours \
		--timeline 0.013,0.008,0.007,0.009,0.02,0.043,0.053,0.055,0.054,0.052,0.052,0.055,0.054,0.055,0.057,0.056,0.057,0.059,0.056,0.047,0.042,0.039,0.032,0.024'	
	os.system(query)

convert_veh_lst = ['veh_od_psrc_convert.csv','veh_od_psrc_wh.csv', 'ped_od.csv']
for veh_csv in convert_veh_lst:
	if 'ped' in veh_csv:
		convert_od_file(veh_csv, veh_csv[:-4]+'.txt','Taz_bigger_Seattle_all_ped_transit.add.xml',veh_csv[:-4]+'.rou.xml',True)
	else:
		convert_od_file(veh_csv, veh_csv[:-4]+'.txt','Taz_bigger_Seattle_all_transit_with_pseudo_link.add.xml',veh_csv[:-4]+'.rou.xml',False)
#convert_od_file('ped_od.csv','ped_od.txt','Taz_bigger_Seattle_all_ped_transit.add.xml','Bigger_Seattle_ped.rou.xml',True)
