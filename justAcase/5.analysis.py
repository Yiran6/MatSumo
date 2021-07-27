import os

import sumolib
import xml.etree.ElementTree as ET

def readSUMO(tripInfoFile):
    # read SUMO output
    dic_od_SUMO = {} # id: departureLink, arrivalLink
    dic_time_SUMO = {} # id: departureTime, arrivalTime, travelTime

    for line in open(tripInfoFile):
        if (line.find('<tripinfo') == 4):
            dataline = line.split(" ")
            tripId = dataline[5].split('=')[1].strip('"')

            # store in dictionary
            departureTime = (dataline[6].split('=')[1].strip('"'))
            departureLink = (dataline[7].split('=')[1].strip('"'))[:-2]
            arrivalTime = dataline[11].split('=')[1].strip('"')
            arrivalLink = (dataline[12].split('=')[1].strip('"'))[:-2]
            dic_od_SUMO[tripId] = [departureLink, arrivalLink]
            dic_time_SUMO[tripId] = [departureTime, arrivalTime]

    return dic_od_SUMO, dic_time_SUMO

def main(sumoRouteInfoFile, sumoTripInfoFile, outfile, sumolinksFile, linkEnterIdsFile, linkEnterTimesFile):

    if os.path.exists(outfile):
        print("File exist:" + outfile)
        return

    # read MATSim origin outputs
    with open(linkEnterIdsFile, "r") as rlinkEnterIdsFile:
        linkEnterIds = rlinkEnterIdsFile.readlines()
        dict_linkEnterIds = {}
        for ilinkEnterIds in linkEnterIds:
            dict_linkEnterIds[ilinkEnterIds.split(":")[0]] = ilinkEnterIds.split(":")[1].split("\t")[1:]

    with open(linkEnterTimesFile, "r") as rlinkEnterTimesFile:
        linkEnterTimes = rlinkEnterTimesFile.readlines()
        dict_linkEnterTimes = {}
        for ilinkEnterTimes in linkEnterTimes:
            dict_linkEnterTimes[ilinkEnterTimes.split(":")[0]] = ilinkEnterTimes.split(":")[1].split("\t")[1:]

    # read SUMO link list
    sumolinks = open(sumolinksFile, "r")
    sumolinks = sumolinks.read().splitlines()
    sumolinks_suMat = {}  # key: SUMO links; value: MATSim links
    for ix in range(len(sumolinks)):
        if ix == 0: continue
        _isumolink = sumolinks[ix].split("\t")
        sumolinks_suMat[_isumolink[0]] = _isumolink[1]

    # read SUMO tripInfo
    dic_route_SUMO, dic_time_SUMO = readSUMO(sumoTripInfoFile)

    outf = open(outfile, "w")
    outf.write("ID\tSUMO departureLink\tSUMO arrivalLink\tSUMO departureTime\tSUMO arrivalTime\tSUMO travelTime"
               + "\tMATSim departureLink\tMATSim arrivalLink\tMATSim departureTime\tMATSim arrivalTime\tMATSim travelTime"
               + "\tdepartureTime difference\tarrivalTime difference\ttravelTime difference\n")
    outf.close()
    with open(outfile, "a") as outf:
        for personSUMO, od in dic_route_SUMO.items():
            departureTimeSUMO = float(dic_time_SUMO[personSUMO][0])
            arrivalTimeSUMO = float(dic_time_SUMO[personSUMO][1])
            departureLaneSUMO = od[0].split("_")[0]
            arrivalLaneSUMO = od[1].split("_")[0]
            departureLaneMATSim = sumolinks_suMat[departureLaneSUMO]
            arrivalLaneMATSim = sumolinks_suMat[arrivalLaneSUMO]
            departureTimeMATSim = arrivalTimeMATSim = 0.

            # find departure time and arrival time in MATSim
            personMATSim = personSUMO.split("_")[0] + "_" + personSUMO.split("_")[1]
            for ix in range(len(dict_linkEnterIds[personMATSim])):
                # departure
                if dict_linkEnterIds[personMATSim][ix] == departureLaneMATSim:
                    departureTimeMATSim = float(dict_linkEnterTimes[personMATSim][ix])
                # arrival
                if dict_linkEnterIds[personMATSim][ix] == arrivalLaneMATSim:
                    arrivalTimeMATSim = float(dict_linkEnterTimes[personMATSim][ix])

            # calculate travel time in SUMO and MATSim
            travelTimeSUMO = arrivalTimeSUMO - departureTimeSUMO
            travelTimeMATSim = arrivalTimeMATSim - departureTimeMATSim

            # output
            """
            SUMO departureLink, SUMO arrivalLink, SUMO departureTime, SUMO arrivalTime, SUMO travelTime,
            MATSim departureLink, MATSim arrivalLink, MATSim departureTime, MATSim arrivalTime, MATSim travelTime,
            departureTime diff, arrivalTime diff, travelTime diff
            """
            outf.write("%s\t%s\t%s\t%f\t%f\t%f\t%s\t%s\t%f\t%f\t%f\t%f\t%f\t%f\n" %
                            (personMATSim, departureLaneSUMO, arrivalLaneSUMO, departureTimeSUMO, arrivalTimeSUMO, travelTimeSUMO,
                             departureLaneMATSim, arrivalLaneMATSim, departureTimeMATSim, arrivalTimeMATSim, travelTimeMATSim,
                             departureTimeSUMO-departureTimeMATSim, arrivalTimeSUMO-arrivalTimeMATSim, travelTimeSUMO-travelTimeMATSim))

    outf.close()

if __name__ == "__main__":
    matsimFolder = "MATSim/"
    sumoFolder = "SUMO/"
    routFolder = matsimFolder + "1.output_extra/"
    sumoRouteInfoFile = sumoFolder + "1.vehicleRoute_Seattle_all.xml"
    sumoTripInfoFile = sumoFolder + "1.tripinfo_Seattle_all.xml"
    sumolinksFile = matsimFolder + "SUMOLinks.txt"
    linkEnterIdsFile = routFolder + "linkEnterIds.txt"
    linkEnterTimesFile = routFolder + "linkEnterTimes.txt"

    outfile = matsimFolder + "1.comparison.txt"
    main(sumoRouteInfoFile, sumoTripInfoFile, outfile, sumolinksFile, linkEnterIdsFile, linkEnterTimesFile)
