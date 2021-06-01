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
		query = 'od2trips -n '+taz_add_file+' -d '+od_txt+' -o '+route_file+' --timeline.day-in-hours \
		--timeline 0.0,0.0,0.0,0.0,0.1,0.1,0.1,0.9,1.0,0.9,0.3,0.3,0.5,0.5,0.3,0.3,0.9,1.0,0.9,0.6,0.2,0.1,0.1,0.1'	
	os.system(query)

convert_od_file('veh_od.csv','veh_od.txt','Taz_bigger_Seattle_all_transit.add.xml','Bigger_Seattle_veh.rou.xml',False)
convert_od_file('ped_od.csv','ped_od.txt','Taz_bigger_Seattle_all_ped_transit.add.xml','Bigger_Seattle_ped.rou.xml',True)

print('Run sumo')
optParser = optparse.OptionParser()
optParser.add_option("--nogui", action="store_true",
                     default=False, help="run the commandline version of sumo")
options, args = optParser.parse_args()

if options.nogui:
    sumoBinary = checkBinary('sumo')
else:
    sumoBinary = checkBinary('sumo-gui')
traci.start([sumoBinary, "-c", "Bigger_Seattle_multi_modes.sumocfg", '--start'])
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
traci.close(wait=False)
sys.stdout.flush()
sys.stderr.flush()

get_data()
