# split trips in MATSim based on the entering time in SUMO
#!/usr/bin/env python

# @author  Jakob Erdmann, Camillo Fillinger, Ohay Angah
# @date    2019-09-27, 2020-06-30

"""
Import person plans from MATSim
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import time

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import sumolib  # noqa
import gzip
import shutil

def unzip(file_gz, file):
    with gzip.open(file_gz, 'rb') as f_in:
        with open(file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    f_in.close()
    return file

def getSec(time_str):
    if time_str == None: return None
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def main(routesFolder, outfile, sumolinksFile, linkExitIdsFile, linkExitTimesFile, tripInfoFile, sumoNetwork):

    # read route file
    routesFile = open(routesFolder + "routes.txt", "r")
    _routes = routesFile.read().splitlines()
    routes = {}
    for iroute in _routes:
        _data = iroute.split(":\t")
        routes[_data[0]] = _data[1].split("\t")

    # read sumolinks
    sumolinks = open(sumolinksFile, "r")
    sumolinks = sumolinks.read().splitlines()
    sumolinks_SuMat = {}  # key: SUMO links; value: MATSim links
    for ix in range(len(sumolinks)):
        if ix == 0: continue
        _isumolink = sumolinks[ix].split("\t")
        sumolinks_SuMat[_isumolink[0]] = _isumolink[1]

    # read linkEnter/ExitIds and linkEnter/ExitTimes
    linkExitIds = open(linkExitIdsFile, "r")
    _linkExitIds = linkExitIds.read().splitlines()
    linkExitIds = {}
    for ilink in _linkExitIds:
        _data = ilink.split(":\t")
        linkExitIds[_data[0]] = _data[1].split("\t")

    linkExitTimes = open(linkExitTimesFile, "r")
    _linkExitTimes = linkExitTimes.read().splitlines()
    linkExitTimes = {}
    for ilink in _linkExitTimes:
        _data = ilink.split(":\t")
        linkExitTimes[_data[0]] = _data[1].split("\t")

    tripType = ['"' + "home" + '"', '"' + "work" + '"']
    tripMode = ['"' + "car" + '"']

    with open(outfile, 'w') as outf:
        # header
        outf.write('<?xml version="1.0" encoding="UTF-8"?>')
        outf.write('<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n')
        outf.write("<plans>\n")

        for person, route in routes.items():
            ix = 0
            routeInSUMOIdx = []
            routeNotInSUMOIdx = []
            for iroute in route:  # iroute = link in the route
                inSUMO = False
                for _, isumolinks in sumolinks_SuMat.items():
                    if iroute == isumolinks:
                        inSUMO = True
                        break
                if inSUMO == True:
                    routeInSUMOIdx.append(ix)
                else:
                    routeNotInSUMOIdx.append(ix)
                ix = ix + 1
                # print("routeNotInSUMOIdx", routeNotInSUMOIdx)
                # print("routeInSUMOIdx", routeInSUMOIdx)

            # write the MATSim plan file
            if len(routeNotInSUMOIdx) > 0:
                # how many of sumo links are in the route
                # print("routeNotInSUMOIdx", routeNotInSUMOIdx)
                # for irouteNotInSUMOIdx in routeNotInSUMOIdx:
                #     print("routeNotInSUMOIdx", route[irouteNotInSUMOIdx])

                # check how many pieces should we split for the route
                _list = []
                list = []
                _listIdx = []
                listIdx = []
                for jx in range(len(routeNotInSUMOIdx)):
                    if (jx==0):
                        _list.append(route[routeNotInSUMOIdx[jx]])

                        _listIdx.append(routeNotInSUMOIdx[jx])
                        if (len(routeNotInSUMOIdx)==1):
                            list.append(_list)
                            listIdx.append(_listIdx)
                        continue
                    if (routeNotInSUMOIdx[jx] - routeNotInSUMOIdx[jx-1] > 1):
                        # split to a new path
                        list.append(_list)
                        _list = []
                        _list.append(route[routeNotInSUMOIdx[jx]])

                        listIdx.append(_listIdx)
                        _listIdx = []
                        _listIdx.append(routeNotInSUMOIdx[jx])
                    else:
                        _list.append(route[routeNotInSUMOIdx[jx]])

                        _listIdx.append(routeNotInSUMOIdx[jx])
                if jx==(len(routeNotInSUMOIdx)-1):
                    list.append(_list)

                    listIdx.append(_listIdx)
                # print("split results:", len(list))

                # check how many pieces should we split for the route
                _SUMOlist = []
                SUMOlist = []
                for jx in range(len(routeInSUMOIdx)):
                    if (jx==0):
                        _SUMOlist.append(route[routeInSUMOIdx[jx]])
                        if (len(routeInSUMOIdx)==1):
                            SUMOlist.append(_SUMOlist)
                        continue
                    if (routeInSUMOIdx[jx] - routeInSUMOIdx[jx-1] > 1):
                        # split to a new path
                        SUMOlist.append(_SUMOlist)
                        _SUMOlist = []
                        _SUMOlist.append(route[routeInSUMOIdx[jx]])
                    else:
                        _SUMOlist.append(route[routeInSUMOIdx[jx]])
                if jx==(len(routeInSUMOIdx)-1):
                    SUMOlist.append(_SUMOlist)
                # print("SUMO links results:", SUMOlist)

                # output the paths
                for jx in range(len(list)):
                    path = list[jx]
                    pathIdx = listIdx[jx]
                    startLink = path[0] # start link of the path
                    startLinkId = pathIdx[0]
                    endLink = path[-1] # end link of the path
                    depart = None

                    idveh_split = "%s_%s" % (person, str(jx))

                    if (jx==0 and startLinkId==0): # get the departure time from MATSim
                        for kx in range(len(linkExitIds[person])):
                            if linkExitIds[person][kx]==startLink:
                                depart = linkExitTimes[person][kx]
                                break
                                # print("depart time", depart)

                    else: # get the departure time from SUMO
                        tripId = departureLane = arrivalTime = arrivalLane = arrivalLaneSUMO = arrivalSpeed = None
                        # get the link that needs to search for: SUMOlist[jx-1][0]
                        for line in open(tripInfoFile):
                            if (line.find('<tripinfo') == 4):
                                dataline = line.split(" ")
                                tripId = dataline[5].split('=')[1].strip('"')
                                departureLaneSUMO = (dataline[7].split('=')[1].strip('"'))[:-2]
                                # find MATSim link by the departureLane
                                departureLane = sumolinks_SuMat[departureLaneSUMO]

                                idveh_split_sumo = "%s_%s" % (person, str(jx-1))
                                if (startLinkId>0 and jx==0): idveh_split_sumo = "%s_%s" % (person, str(jx))
                                if (idveh_split_sumo == tripId):
                                    if (jx-1 < 0):
                                        if (departureLane == (SUMOlist[jx])[0]):
                                            arrivalTime = dataline[11].split('=')[1].strip('"')
                                            arrivalLaneSUMO = (dataline[12].split('=')[1].strip('"'))
                                            arrivalLane = (dataline[12].split('=')[1].strip('"'))[:-2]
                                            arrivalSpeed = dataline[14].split('=')[1].strip('"')
                                            # print("arrivalTime", arrivalTime, "arrivalLane", arrivalLane, "arrivalSpeed", arrivalSpeed)
                                            break
                                    else:
                                        if (departureLane == (SUMOlist[jx - 1])[0]):
                                            arrivalTime = dataline[11].split('=')[1].strip('"')
                                            arrivalLaneSUMO = (dataline[12].split('=')[1].strip('"'))
                                            arrivalLane = (dataline[12].split('=')[1].strip('"'))[:-2]
                                            arrivalSpeed = dataline[14].split('=')[1].strip('"')
                                            # print("arrivalTime", arrivalTime, "arrivalLane", arrivalLane, "arrivalSpeed", arrivalSpeed)
                                            break

                        depart = float(arrivalTime)
                        # # calculate the departure time in MATSim from SUMO speed and SUMO distance
                        # if (arrivalLaneSUMO!=None):
                        #     laneLength = None
                        #     # find the link length from SUMO network file
                        #     for line in open(sumoNetwork):
                        #         if (line.find('<lane') == 8):
                        #             dataline = line.split(" ")
                        #             _link = (dataline[9].split('=')[1].strip('"'))
                        #             if (_link==arrivalLaneSUMO):
                        #                 laneLength = (dataline[12].split('=')[1].strip('"'))
                        #                 break
                        #     if (laneLength!=None):
                        #         depart = float(arrivalTime) + float(laneLength)/float(arrivalSpeed)

                    depart_work = "%s" % (time.strftime('%H:%M:%S', time.gmtime(float(depart) + 12*3600)))
                    depart = "%s" % (time.strftime('%H:%M:%S', time.gmtime(float(depart))))
                    fromLink = "%s" % (startLink)
                    toLink = "%s" % (endLink)

                    # write data
                    outf.write('\t<person id="%s">\n' % idveh_split)
                    outf.write("\t\t<plan>\n")
                    # # activities: home
                    outf.write('\t\t\t<act type=%s link="%s" end_time="%s" />\n' % (tripType[0], fromLink, depart))
                    outf.write("\t\t\t<leg mode=%s>\n" % tripMode[0])
                    outf.write("\t\t\t\t<route> </route>\n")
                    outf.write("\t\t\t</leg>\n")
                    # activities: work
                    outf.write('\t\t\t<act type=%s link="%s" end_time="%s" />\n' % (tripType[1], toLink, depart_work))
                    outf.write("\t\t\t<leg mode=%s>\n" % tripMode[0])
                    outf.write("\t\t\t\t<route> </route>\n")
                    outf.write("\t\t\t</leg>\n")
                    # activities: home
                    outf.write('\t\t\t<act type=%s link="%s"/>\n' % (tripType[0], fromLink))
                    outf.write("\t\t</plan>\n")
                    outf.write("\t</person>\n")
        outf.write("</plans>\n")
    outf.close()


if __name__ == "__main__":
    matsimFolder = "MATSim/"
    sumoFolder = "SUMO/"
    routFolder = matsimFolder + "1.output_extra/"
    outfile = matsimFolder + "sumo_ToMATSim_plans.xml"
    tripInfoFile = sumoFolder + "tripinfo_Seattle_all.xml"
    linkExitIdsFile = routFolder + "linkExitIds.txt"
    linkExitTimesFile = routFolder + "linkExitTimes.txt"
    sumolinks = matsimFolder + "SUMOLinks.txt"
    sumoNetwork = sumoFolder + "/0.fmYiran/Network_check_Ped/Seattle02262021_veh_ped.net.xml"
    carsOnly = True
    main(routFolder, outfile, sumolinks, linkExitIdsFile, linkExitTimesFile, tripInfoFile, sumoNetwork)

