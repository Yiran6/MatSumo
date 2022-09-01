# -*- coding: utf-8 -*-
import os
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import random
import numpy as np
import sumolib
import math
from joblib import dump, load
import pandas as pd

# main entry point
def get_data():

    vehDelay_avg =[]
    waitingCount_avg =[]
    averageSpeed_avg =[]

    # retrain the PLS
    vehDelay = {}
    waitingCount = {}
    averageSpeed = {}

    for i in range(24):
        vehDelay[i] = []
        waitingCount[i] = []
        averageSpeed[i] = []

    for veh in sumolib.output.parse_fast("tripinfo_Bigger_Seattle.xml", 'tripinfo', ['id','depart','duration', 'routeLength', 'waitingTime','waitingCount','timeLoss']):
        print(veh.id)
        hour_index = float(veh.depart)//3600
        averageSpeed[hour_index].append(float(veh.routeLength)/float(veh.duration))
        vehDelay[hour_index].append(float(veh.waitingTime))
        waitingCount[hour_index].append(float(veh.waitingCount))

    for hour_index in range(24):
        vehDelay_avg.append(sum(vehDelay[hour_index])/(len(vehDelay[hour_index])+1e-8))
        waitingCount_avg.append(sum(waitingCount[hour_index])/(len(waitingCount[hour_index])+1e-8))
        averageSpeed_avg.append(sum(averageSpeed[hour_index])/(len(averageSpeed[hour_index])+1e-8))

    data_all = np.array([vehDelay_avg, waitingCount_avg, averageSpeed_avg])

    np.savetxt('data_stats_ph.csv', data_all, delimiter = ',')
