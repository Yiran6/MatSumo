# Program to run the Seattle downtown network
import numpy as np
import os
import traci
import sys
import optparse
from sumolib import checkBinary
from numpy import genfromtxt
from data_extract import get_data

print('Run sumo')
optParser = optparse.OptionParser()
optParser.add_option("--nogui", action="store_true",
                     default=True, help="run the commandline version of sumo")
options, args = optParser.parse_args()

if options.nogui:
    sumoBinary = checkBinary('sumo')
else:
    sumoBinary = checkBinary('sumo-gui')
traci.start([sumoBinary, "-c", "Bigger_Seattle_multi_modes_withsignal_convert.sumocfg", '--start'])
t = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    print(t)
    t += 1
    
traci.close(wait=False)
sys.stdout.flush()
sys.stderr.flush()

get_data()


#get_data()
