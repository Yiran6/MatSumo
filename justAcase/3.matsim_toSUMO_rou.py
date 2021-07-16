# split trips in MATSim that are in SUMOLinks
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

def main(planfile, planfile_gz, eventfile_gz, eventfile, outfile, sumolinks, carsOnly):

    planfile = unzip(planfile_gz, planfile)
    eventfile = unzip(eventfile_gz, eventfile)
    sumolinks = open(sumolinks, "r")
    sumolinks = ((sumolinks.read().split('\t'))[0].split('\n'))[:-1]

    with open(outfile, 'w') as outf:
        sumolib.writeXMLHeader(outf, "$Id: matsim_toSUMO_rou.py v1 2020-07-01 15:41:56$", "routes")  # noqa
        output_dict = {}
        for person in sumolib.output.parse(planfile, 'person'):
            vehIndex = 0
            print("personID:", person.id)
            # looking for first selected trip
            for trip_id in range(len(person.plan)):
                plan = person.plan[trip_id]
                if plan.selected == "yes": break

            # write vehicles
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

                # write the SUMO route file
                if len(routeInSUMOIdx) > 0:
                    # how many of sumo links are in the route
                    print("routeInSUMOIdx", routeInSUMOIdx)
                    # for irouteInSUMOIdx in routeInSUMOIdx:
                    #     print("routeInSUMO", route[irouteInSUMOIdx])

                    # check how many pieces should we split for the route
                    _list = []
                    list = []
                    for jx in range(len(routeInSUMOIdx)):
                        if (jx==0):
                            _list.append(route[routeInSUMOIdx[jx]])
                            continue
                        if (routeInSUMOIdx[jx] - routeInSUMOIdx[jx-1] > 1):
                            # split to a new path
                            list.append(_list)
                            _list = []
                            _list.append(route[routeInSUMOIdx[jx]])
                        else:
                            _list.append(route[routeInSUMOIdx[jx]])
                    if jx==(len(routeInSUMOIdx)-1):
                        list.append(_list)
                    # print("split results:", list)

                    # output the paths
                    for jx in range(len(list)):
                        path = list[jx]
                        startLink = path[0]
                        endLink = path[-1]

                        idveh = "%s_%s" % (idveh, str(jx))

                        # get the departure time
                        cntEvent = -1
                        for event in sumolib.output.parse(eventfile, 'event', heterogeneous=True):
                            if (event.person == person.id or event.vehicle == person.id) and event.link == startLink and (event.type == "entered link" or event.type == "vehicle enters traffic"):
                                cntEvent = cntEvent + 1
                                # print("cntEvent", cntEvent, "vehIndex", vehIndex)
                                if (cntEvent==vehIndex):
                                    depart = event.time
                                    break
                                # print("depart time", event.time)
                        output_dict[float(depart)] = '   <trip id="%s" depart="%s" from="%s" to="%s"/>\n' % (idveh, depart, startLink, endLink)
                        # outf.write('   <trip id="%s" depart="%s" from="%s" to="%s"/>\n' % (idveh, depart, startLink, endLink))
                        # print(output_dict)
                vehIndex = vehIndex + 1

        # output the dictionary
        for ix in sorted(output_dict.keys()):
            outf.write(output_dict[ix])
        outf.write('</routes>\n')
    outf.close()


if __name__ == "__main__":
    matsimFolder = "MATSim/"
    gz_folder = matsimFolder + "1.output/"
    planfile = gz_folder + "output_plans.xml"
    planfile_gz = gz_folder + "output_plans.xml.gz"
    eventfile = gz_folder + "output_events.xml"
    eventfile_gz = gz_folder + "output_events.xml.gz"
    outfile = "SUMO/matsim_ToSUMO.rou.xml"
    sumolinks = matsimFolder + "SUMOLinks.txt"
    carsOnly = True
    main(planfile, planfile_gz, eventfile_gz, eventfile, outfile, sumolinks, carsOnly)
