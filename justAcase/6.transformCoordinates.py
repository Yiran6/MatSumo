# netconvert --sumo-net-file SUMO/0.fmYiran/Network_check_Ped/Seattle02262021_veh_ped.net.xml --matsim-output MATSim/text.xml

import sumolib
import pyproj

_projections = {}

def SUMOLinksToWGS84(sumolinksFile, outFile, sumoNet):
    # read route file
    netFile = open(sumolinksFile, "r")
    netData = netFile.readlines()
    sumoNet = sumolib.net.readNet(sumoNet)

    with open(outFile, "w") as outf:

        for ix in range(len(netData)):
            if ix < 5:
                outf.write(netData[ix])
            elif ix >= 5 and ix <= 3460:
                id = (netData[ix].split("\n"))[0].strip("/>").split(" ")[7].split("=")[1].strip('"')
                x = float((netData[ix].split("\n"))[0].strip("/>").split(" ")[8].split("=")[1].strip('"'))
                y = float((netData[ix].split("\n"))[0].strip("/>").split(" ")[9].split("=")[1].strip('"'))

                # convert the coord to WGS84
                lon, lat = sumoNet.convertXY2LonLat(x, y)

                # output
                outf.write('      <node id="%s" x="%f" y="%f"/>\n' % (id, lon, lat))
            else:
                outf.write(netData[ix])

"""
Use the z, l, x, y = project(coord) with coord = (lng, lat) to convert your latitude and longitude to get UTM coordinates 
and the zone (z) and letter (l). use lng, lat = unproject(z, l, x, y) to get back latitude and longitude from UTM.
"""
def zone(coordinates):
    if 56 <= coordinates[1] < 64 and 3 <= coordinates[0] < 12:
        return 32
    if 72 <= coordinates[1] < 84 and 0 <= coordinates[0] < 42:
        if coordinates[0] < 9:
            return 31
        elif coordinates[0] < 21:
            return 33
        elif coordinates[0] < 33:
            return 35
        return 37
    return int((coordinates[0] + 180) / 6) + 1

def letter(coordinates):
    return 'CDEFGHJKLMNPQRSTUVWXX'[int((coordinates[1] + 80) / 8)]

def project(coordinates):
    z = zone(coordinates)
    l = letter(coordinates)
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    x, y = _projections[z](coordinates[0], coordinates[1])
    if y < 0:
        y += 10000000
    return z, l, x, y

def unproject(z, l, x, y):
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    if l < 'N':
        y -= 10000000
    lng, lat = _projections[z](x, y, inverse=True)
    return (lng, lat)

def MATSimLinksToUTM(lon, lat):
    coord = (lon, lat)
    z, l, x, y = project(coord)
    return x, y


def main(sumolinksFile, outFile, sumoNet, matsimNetFile, outNewMatsimNetFile):
    # SUMOLinksToWGS84(sumolinksFile, outFile, sumoNet)

    # read route file and output the UTM coordinates
    netFile = open(matsimNetFile, "r")
    netData = netFile.readlines()

    with open(outNewMatsimNetFile, "w") as outf:

        for ix in range(len(netData)):
            if ix < 7:
                outf.write(netData[ix])
            elif ix >= 7 and ix <= 214512:
                if ix%2 == 1:
                    id = (netData[ix].split("\n"))[0].strip("/>").split(" ")[1].split("=")[1].strip('"')
                    lon = float((netData[ix].split("\n"))[0].strip("/>").split(" ")[2].split("=")[1].strip('"'))
                    lat = float((netData[ix].split("\n"))[0].strip("/>").split(" ")[3].split("=")[1].strip('"'))

                    # convert the coord to UTM from WGS84
                    x, y = MATSimLinksToUTM(lon, lat)

                    # output
                    outf.write('      <node id="%s" x="%f" y="%f"/>\n' % (id, x, y))
                # else:
                #     outf.write(netData[ix])
            else:
                outf.write(netData[ix])


if __name__ == "__main__":
    matsimFolder = "MATSim/"
    sumolinksFile = matsimFolder + "text.xml"
    outFile = matsimFolder + "text-MATSim.xml"
    sumoNet = "SUMO/0.fmYiran/Network_check_Ped/Seattle02262021_veh_ped.net.xml"
    matsimNetFile = matsimFolder + "Great_Seattle_addOn_ToOSM_ToMATSim.xml"
    outNewMatsimNetFile = matsimFolder + "Great_Seattle_addOn_ToOSM_ToMATSim_UTM.xml"
    main(sumolinksFile, outFile, sumoNet, matsimNetFile, outNewMatsimNetFile)