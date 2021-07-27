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
import pandas as pd

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

def main(routesFolder, outfile, sumolinksFile, linkEnterIdsFile, linkEnterTimesFile):

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
    sumolinks_matSu = {} # key: MATSim links; value: SUMO links
    for ix in range(len(sumolinks)):
        if ix==0: continue
        _isumolink = sumolinks[ix].split("\t")
        sumolinks_matSu[_isumolink[1]] = _isumolink[0]

    # read linkEnter and linkEnter
    linkEnterIds = open(linkEnterIdsFile, "r")
    _linkEnterIds = linkEnterIds.read().splitlines()
    linkEnterIds = {}
    for ilink in _linkEnterIds:
        _data = ilink.split(":\t")
        linkEnterIds[_data[0]] = _data[1].split("\t")

    linkEnterTimes = open(linkEnterTimesFile, "r")
    _linkEnterTimes = linkEnterTimes.read().splitlines()
    linkEnterTimes = {}
    for ilink in _linkEnterTimes:
        _data = ilink.split(":\t")
        linkEnterTimes[_data[0]] = _data[1].split("\t")

    # check each route to see if the person entered SUMO links
    with open(outfile, 'w') as outf:
        sumolib.writeXMLHeader(outf, "$Id: matsim_toSUMO_rou.py v1 2020-07-01 15:41:56$", "routes")  # noqa
        output_dict = []
        for person, route in routes.items():
            ix = 0
            routeInSUMOIdx = []
            routeNotInSUMOIdx = []
            for iroute in route: # iroute = link in the route
                inSUMO = False
                for isumolinks, _ in sumolinks_matSu.items():
                    if iroute == isumolinks:
                        inSUMO = True
                        break
                if inSUMO == True:
                    routeInSUMOIdx.append(ix)
                else:
                    routeNotInSUMOIdx.append(ix)
                ix = ix + 1

            # write the SUMO route file
            if len(routeInSUMOIdx) > 0:
                # how many sumo links are in the route
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
                    startLinkMATsim = path[0]
                    endLinkMATSim = path[-1]

                    # find sumo links
                    startLink = sumolinks_matSu[startLinkMATsim]
                    endLink = sumolinks_matSu[endLinkMATSim]

                    idveh = "%s_%s" % (person, str(jx))

                    # get the departure time
                    depart = 0
                    for ix in range(len(linkEnterIds[person])):
                        if startLinkMATsim==linkEnterIds[person][ix]:
                            depart = linkEnterTimes[person][ix]
                            break
                    string = ('   <trip id="%s" depart="%s" from="%s" to="%s"/>\n' % (idveh, depart, startLink, endLink))
                    output_dict.append([depart, string])

        # output the list
        df = pd.DataFrame(output_dict, columns=['Depart', 'Str'])
        df_sorted = df.sort_values(by=['Depart'])
        df_sorted = df_sorted.reset_index(drop=True)
        for ix in range(len(df_sorted)):
            outf.write(df_sorted.loc[ix]['Str'])
        outf.write('</routes>\n')


if __name__ == "__main__":
    matsimFolder = "MATSim/"
    routFolder = matsimFolder + "1.output_extra/"
    outfile = "SUMO/1.matsim_ToSUMO.rou.xml"
    sumolinksFile = matsimFolder + "SUMOLinks.txt"
    linkEnterIdsFile = routFolder + "linkEnterIds.txt"
    linkEnterTimesFile = routFolder + "linkEnterTimes.txt"
    main(routFolder, outfile, sumolinksFile, linkEnterIdsFile, linkEnterTimesFile)
