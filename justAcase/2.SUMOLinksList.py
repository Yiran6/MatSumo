import sumolib
import numpy as np
from math import sin, cos, sqrt, atan2, radians

def latLonDist(lat1, lon1, lat2, lon2):
    # function for calculating ground distance between two lat-long locations
    R = 6373.0 # approximate radius of earth in km.

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = float(format( R * c , '.2f' )) #rounding. From https://stackoverflow.com/a/28142318/4355695
    return distance

def readMATSimNet(matsimNet):
    nodes = {} # key:ID; value: lon, lat
    links = {} # key: ID; value: fromNodeId, fromNodeLon, fromNodeLat, toNodeId, toNodeLon, toNodeLat, freeSpeed, linkLength

    # read MATSim nodes
    for node in sumolib.xml.parse(matsimNet, ['node']):
        nodeID = node.id
        nodeLon, nodeLat = float(node.x), float(node.y)
        if nodeID not in nodes:
            nodes[nodeID] = [nodeLon, nodeLat]
    print("MATSim network has %s nodes" % len(nodes))

    # read MATSim links
    for link in sumolib.xml.parse(matsimNet, ['link']):
        linkID = link.id
        fromNodeId = link.attr_from
        toNodeId = link.to
        freeSpeed = float(link.freespeed)
        linkLength = float(link.length)

        if linkID not in links:
            # determine fromNodeId, fromNodeLon, fromNodeLat, toNodeId, toNodeLon, toNodeLat, freeSpeed, linkLength
            fromNodeLon = nodes[fromNodeId][0]
            fromNodeLat = nodes[fromNodeId][1]
            toNodeLon = nodes[toNodeId][0]
            toNodeLat = nodes[toNodeId][1]
            links[linkID] = [fromNodeId, fromNodeLon, fromNodeLat, toNodeId, toNodeLon, toNodeLat, freeSpeed, linkLength]
    print("MATSim network has %s links" % len(links))
    return links

def main(matsimNet, sumoNet, outputFile):
    matsimNetDictionary = readMATSimNet(matsimNet)
    SUMOedgeCnt = 0
    sumoNetObj = sumolib.net.readNet(sumoNet)

    def checkRoutes(edgeId):
        fromnode = sumoNetObj.getEdge(edgeId).getFromNode().getID()
        tonode = sumoNetObj.getEdge(edgeId).getFromNode().getID()
        fromNodecoordX, fromNodecoordY = sumoNetObj.getNode(fromnode).getCoord()
        toNodecoordX, toNodecoordY = sumoNetObj.getNode(tonode).getCoord()
        fromNodecoordLon, fromNodecoordLat = sumoNetObj.convertXY2LonLat(fromNodecoordX, fromNodecoordY)
        toNodecoordLon, toNodecoordLat = sumoNetObj.convertXY2LonLat(toNodecoordX, toNodecoordY)
        edgeSpeedlimit = sumoNetObj.getEdge(edgeId).getSpeed()
        edgeLength = sumoNetObj.getEdge(edgeId).getLength()
        return fromNodecoordLon, fromNodecoordLat, toNodecoordLon, toNodecoordLat, edgeSpeedlimit, edgeLength

    with open(outputFile, 'w') as outputMATSumo:
        outputMATSumo.write("SUMOLinkID\tMATSimLinkID\tdistance\n")

        # read SUMO links
        for edge in sumolib.xml.parse(sumoNet, ['edge']):
            edgeID = edge.id
            # check if the disallow and allow attributes have 'private'
            # if any lanes under the edge can allow 'private' vehicles, we include the SUMO edge
            lanes = edge['lane']
            fromNodeCoordLon = fromNodeCoordLat = toNodeCoordLon = toNodeCoordLat = edgeSpeedlimit = edgeLength = 0.
            if edge.function is None:
                for ilane in lanes:
                    # check 'allow' attribute
                    if ilane.allow is not None and ilane.disallow is None:
                        # only check 'allow'
                        if "private" in ilane.allow:
                            # include checking the SUMO edge
                            fromNodeCoordLon, fromNodeCoordLat, toNodeCoordLon, toNodeCoordLat, edgeSpeedlimit, edgeLength = checkRoutes(edgeID)
                            break
                    elif ilane.disallow is not None and ilane.allow is None:
                        # only check 'disallow'
                        if "private" not in ilane.disallow:
                            # include checking the SUMO edge
                            fromNodeCoordLon, fromNodeCoordLat, toNodeCoordLon, toNodeCoordLat, edgeSpeedlimit, edgeLength = checkRoutes(edgeID)
                            break
                    elif ilane.allow is not None and ilane.disallow is not None:
                        # check 'allow' and 'disallow'
                        if "private" in ilane.allow and "private" not in ilane.disallow:
                            # include checking the SUMO edge
                            fromNodeCoordLon, fromNodeCoordLat, toNodeCoordLon, toNodeCoordLat, edgeSpeedlimit, edgeLength = checkRoutes(edgeID)
                            break

                SUMOedgeCnt += 1

                if fromNodeCoordLon != 0:
                    linkIDList = []
                    distanceList = []
                    # find the closest MATSim link
                    for linkID, [fromNodeId, fromNodeLon, fromNodeLat, toNodeId, toNodeLon, toNodeLat, freeSpeed, linkLength] in matsimNetDictionary.items():
                        linkIDList.append(linkID)
                        distanceFrom = latLonDist(fromNodeCoordLon, fromNodeCoordLat, fromNodeLon, fromNodeLat)
                        distanceTo = latLonDist(toNodeCoordLon, toNodeCoordLat, toNodeLon, toNodeLat)
                        if freeSpeed == 0.:
                            distanceFrom = distanceTo = 999.
                        distanceList.append(distanceFrom + distanceTo)

                    indexMin = np.argmin(distanceList)
                    print("MATSim link %s speed is %5.3f; length is %5.3f:" % (linkIDList[indexMin], matsimNetDictionary[linkIDList[indexMin]][6], matsimNetDictionary[linkIDList[indexMin]][7]))
                    print("SUMO link %s speed is %5.3f; length is %5.3f:" % (edgeID, edgeSpeedlimit, edgeLength))
                    print("====")

                    # output
                    outputMATSumo.write("%s\t%s\t%8.5f\n" % (edgeID, linkIDList[indexMin], distanceList[indexMin]))
                        # if edgeID=="-103052747": break
        print("SUMO network has %s links" % SUMOedgeCnt)

if __name__ == "__main__":
    # MATSim nets
    MATSimFolder = "MATSim/"
    MATSimNet = MATSimFolder + 'Great_Seattle_addOn_ToOSM_ToMATSim.xml'

    outputFile = "MATSim/SUMOLinks.txt"

    # SUMO nets
    SUMOFolder = "SUMO/0.fmYiran/Network_check_Ped/"
    SUMONet = SUMOFolder + 'Seattle02262021_veh_ped.net.xml'

    main(MATSimNet, SUMONet, outputFile)
