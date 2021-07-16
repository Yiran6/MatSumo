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

def main(planfile, planfile_gz, eventfile_gz, eventfile, outfile, sumolinks, carsOnly, tripInfoFile, sumoNetwork):

    planfile = unzip(planfile_gz, planfile)
    eventfile = unzip(eventfile_gz, eventfile)
    sumolinks = open(sumolinks, "r")
    sumolinks = ((sumolinks.read().split('\t'))[0].split('\n'))[:-1]

    tripType = ['"' + "home" + '"', '"' + "work" + '"']
    tripMode = ['"' + "car" + '"']

    with open(outfile, 'w') as outf:
        # header
        outf.write('<?xml version="1.0" encoding="UTF-8"?>')
        outf.write('<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n')
        outf.write("<plans>\n")

        for person in sumolib.output.parse(planfile, 'person'):
            vehIndex = 0
            print("personID:", person.id)
            # looking for first selected trip
            for trip_id in range(len(person.plan)):
                plan = person.plan[trip_id]
                if plan.selected == "yes": break

            # vehicles
            vehicleslist = []
            untillist = []

            for leg in plan.leg:
                depart = getSec(leg.dep_time) if carsOnly else "triggered"
                if depart == None:
                    depart = getSec(plan.activity[vehIndex].end_time)

                idveh = "%s_%s" % (person.id, vehIndex)
                # check if this vehicle goes into SUMO region -- use eventfile to get departure time
                route = (leg.route[0].getText()).split()

                eventInSUMO = []
                routeInSUMOIdx = []
                routeNotInSUMOIdx = []
                ix = 0
                for iroute in route: # iroute = link in the route
                    inSUMO = False
                    for isumolinks in sumolinks:
                        if iroute == isumolinks:
                            inSUMO = True
                            # print("check", person.id, iroute, isumolinks)
                            break
                    if inSUMO == True:
                        routeInSUMOIdx.append(ix)
                        # print("eventInSUMO", eventInSUMO)
                    else:
                        routeNotInSUMOIdx.append(ix)
                    # print("cntRoute", ix)
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

                        idveh_split = "%s_%s" % (idveh, str(jx))

                        if (jx==0 and startLinkId==0): # get the departure time from MATSim
                            cntEvent = -1
                            for event in sumolib.output.parse(eventfile, 'event', heterogeneous=True):
                                if (event.person == person.id or event.vehicle == person.id) and event.link == startLink and (event.type == "entered link" or event.type == "vehicle enters traffic"):
                                    cntEvent = cntEvent + 1
                                    # print("cntEvent", cntEvent, "vehIndex", vehIndex)
                                    if (cntEvent==vehIndex):
                                        depart = event.time
                                        break
                                    # print("depart time", depart)

                        else: # get the departure time from SUMO
                            tripId = departureLane = arrivalTime = arrivalLane = arrivalLaneSUMO = arrivalSpeed = None
                            # get the link that needs to search for: SUMOlist[jx-1][0]
                            for line in open(tripInfoFile):
                                if (line.find('<tripinfo') == 4):
                                    dataline = line.split(" ")
                                    tripId = dataline[5].split('=')[1].strip('"')
                                    departureLane = (dataline[7].split('=')[1].strip('"'))[:-2]

                                    idveh_split_sumo = "%s_%s" % (idveh, str(jx-1))
                                    if (startLinkId>0 and jx==0): idveh_split_sumo = "%s_%s" % (idveh, str(jx))
                                    if (idveh_split_sumo==tripId and departureLane==(SUMOlist[jx-1])[0]):
                                        arrivalTime = dataline[11].split('=')[1].strip('"')
                                        arrivalLaneSUMO = (dataline[12].split('=')[1].strip('"'))
                                        arrivalLane = (dataline[12].split('=')[1].strip('"'))[:-2]
                                        arrivalSpeed = dataline[14].split('=')[1].strip('"')
                                        # print("arrivalTime", arrivalTime, "arrivalLane", arrivalLane, "arrivalSpeed", arrivalSpeed)
                                        break

                            # calculate the departure time in MATSim from SUMO speed and SUMO distance
                            if (arrivalLaneSUMO!=None):
                                laneLength = None
                                # find the link length from SUMO network file
                                for line in open(sumoNetwork):
                                    if (line.find('<lane') == 8):
                                        dataline = line.split(" ")
                                        _link = (dataline[9].split('=')[1].strip('"'))
                                        if (_link==arrivalLaneSUMO):
                                            laneLength = (dataline[12].split('=')[1].strip('"'))
                                            break
                                if (laneLength!=None):
                                    depart = float(arrivalTime) + float(laneLength)/float(arrivalSpeed)

                        depart_work = "%s" % (time.strftime('%H:%M:%S', time.gmtime(float(depart) + 24*3600)))
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
                vehIndex = vehIndex + 1
        outf.write("</plans>\n")
    outf.close()


if __name__ == "__main__":
    matsimFolder = "MATSim/"
    sumoFolder = "SUMO/"
    gz_folder = matsimFolder + "1.output/"
    planfile = gz_folder + "output_plans.xml"
    planfile_gz = gz_folder + "output_plans.xml.gz"
    eventfile = gz_folder + "output_events.xml"
    eventfile_gz = gz_folder + "output_events.xml.gz"
    outfile = matsimFolder + "sumo_ToMATSim_plans.xml"
    tripInfoFile = sumoFolder + "tripinfo_Seattle_all.xml"
    sumolinks = matsimFolder + "SUMOLinks.txt"
    sumoNetwork = sumoFolder + "SUMOLinks.net.xml"
    carsOnly = True
    main(planfile, planfile_gz, eventfile_gz, eventfile, outfile, sumolinks, carsOnly, tripInfoFile, sumoNetwork)
#
#
#
# def main(out_route, routes_doc, network):
#     outfile = open(out_route, 'w')
#     # header
#     outfile.write('<?xml version="1.0" encoding="UTF-8"?>')
#     outfile.write('<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n')
#     outfile.write("<plans>\n")
#
#     for line in open(routes_doc):
#
#         if (line.find('<?xml') == 1):
#             outfile.write(line)
#         elif (line.find('<trip') > 0):
#             # find trip info
#             dataline = line.split(" ")
#             id = dataline[5].split('=')[1]
#             departTimeRaw = float(dataline[6].split('=')[1].strip('"'))
#             departTime = '"' + str(time.strftime('%H:%M:%S', time.gmtime(departTimeRaw))) + '"'
#             departTime_work = departTimeRaw + 4*3600
#             departTime_work = '"' + str(time.strftime('%H:%M:%S', time.gmtime(departTime_work))) + '"'
#
#             fromLink = '"' + str(dataline[7].split('=')[1].strip('"')) + '"'
#             toLink = '"' + str((dataline[8].split('=')[1].strip('"'))[:-4]) + '"'
#
#             # node_id_fm = dataline[7].split('=')[1].strip('"')
#             # node_id_to = (dataline[8].split('=')[1].strip('"'))[:-4]
#
#             # # find link using node
#             # link_id = findLink(node_id_fm)
#             # fromLink = '"' + str(link_id) + '"'
#             # print("from", fromLink)
#             #
#             # # find link using node
#             # link_id = findLink(node_id_to)
#             # toLink = '"' + str(link_id) + '"'
#             # print("to", toLink)
#
#             # write data
#             outfile.write("\t<person id=%s>\n" % id)
#             outfile.write("\t\t<plan>\n")
#             # activities: home
#             outfile.write("\t\t\t<act type=%s link=%s end_time=%s />\n" % (tripType[0], fromLink, departTime))
#             outfile.write("\t\t\t<leg mode=%s>\n" % tripMode[0])
#             outfile.write("\t\t\t\t<route> </route>\n")
#             outfile.write("\t\t\t</leg>\n")
#             # activities: work
#             outfile.write("\t\t\t<act type=%s link=%s end_time=%s />\n" % (tripType[1], toLink, departTime_work))
#             outfile.write("\t\t\t<leg mode=%s>\n" % tripMode[0])
#             outfile.write("\t\t\t\t<route> </route>\n")
#             outfile.write("\t\t\t</leg>\n")
#             # activities: home
#             outfile.write("\t\t\t<act type=%s link=%s/>\n" % (tripType[0], fromLink))
#             # break
#
#             outfile.write("\t\t</plan>\n")
#             outfile.write("\t</person>\n")
#     outfile.write("</plans>\n")
#
#     outfile.close()
#
# if __name__ == "__main__":
#     DEPART_ATTRS = {'vehicle': 'depart', 'flow': 'begin', 'person': 'depart'}
#
#     tripType = ['"' + "home" + '"', '"' + "work" + '"']
#     tripMode = ['"' + "car" + '"']
#     duration = '"' + "00:40" + '"'
#     deltaT = 1.0 # seconds per time step in SUMO
#
#     out_route = "MATSim\Seattle_Streets_ToJOSMUTM_fixed_OSM_ToMATSim_SUMORoute2Plan.xml"
#     routes_doc = "SUMO\Seattle_Streets_ToJOSMUTM_fixed_OSM_ToMATSim.rou.xml"
#     network = "MATSim\Seattle_Streets_ToJOSMUTM_fixed_OSM_ToMATSim.xml"
#     tripInfoFile = "SUMO\tripinfo_Seattle_all.xml"
#
#     main(out_route, routes_doc, network, tripInfoFile)
