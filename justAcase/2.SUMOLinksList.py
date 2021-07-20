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

    with open(outputFile, 'w') as outputMATSumo:
        outputMATSumo.write("SUMOLinkID\tMATSimLinkID\n")

        # read SUMO links
        for edge in sumolib.xml.parse(sumoNet, ['edge']):
            edgeID = edge.id
            if edge.function==None:
                fromNode = sumoNetObj.getEdge(edgeID).getFromNode().getID()
                toNode = sumoNetObj.getEdge(edgeID).getFromNode().getID()
                fromNodeCoordX, fromNodeCoordY = sumoNetObj.getNode(fromNode).getCoord()
                toNodeCoordX, toNodeCoordY = sumoNetObj.getNode(toNode).getCoord()
                fromNodeCoordLon, fromNodeCoordLat = sumoNetObj.convertXY2LonLat(fromNodeCoordX, fromNodeCoordY)
                toNodeCoordLon, toNodeCoordLat = sumoNetObj.convertXY2LonLat(toNodeCoordX, toNodeCoordY)
                edgeSpeedlimit = sumoNetObj.getEdge(edgeID).getSpeed()
                edgeLength = sumoNetObj.getEdge(edgeID).getLength()
                SUMOedgeCnt += 1

                linkIDList = []
                distanceList = []
                # find the closest MATSim link
                for linkID, [fromNodeId, fromNodeLon, fromNodeLat, toNodeId, toNodeLon, toNodeLat, freeSpeed, linkLength] in matsimNetDictionary.items():
                    linkIDList.append(linkID)
                    distanceFrom = latLonDist(fromNodeCoordLon, fromNodeCoordLat, fromNodeLon, fromNodeLat)
                    distanceTo = latLonDist(toNodeCoordLon, toNodeCoordLat, toNodeLon, toNodeLat)
                    distanceList.append(distanceFrom + distanceTo)
                indexMin = np.argmin(distanceList)
                print("MATSim link %s speed is %5.3f; length is %5.3f:" % (linkIDList[indexMin], matsimNetDictionary[linkIDList[indexMin]][6], matsimNetDictionary[linkIDList[indexMin]][7]))
                print("SUMO link %s speed is %5.3f; length is %5.3f:" % (edgeID, edgeSpeedlimit, edgeLength))
                print("====")

                # output
                outputMATSumo.write("%s\t%s\n" % (edgeID, linkIDList[indexMin]))
                # if edgeID=="-103052747": break
        print("SUMO network has %s links" % SUMOedgeCnt)

if __name__ == "__main__":
    # MATSim nets
    MATSimFolder = "MATSim/"
    MATSimNet = MATSimFolder + 'streets_sdot_fixed_ToMATSim.xml'

    outputFile = "MATSim/SUMOLinks.txt"

    # SUMO nets
    SUMOFolder = "SUMO/0.fmYiran/Network_check_Ped/"
    SUMONet = SUMOFolder + 'Seattle02262021_veh_ped.net.xml'

    main(MATSimNet, SUMONet, outputFile)
