# check if MATSim network can work

import xml.etree.ElementTree as ET
import json
import random
import time

folder = "MATSim/"
outputFolder = "MATSim/"
tree = ET.parse(folder + "/" + "streets_sdot_fixed_ToMATSim.xml")
root = tree.getroot()

allLinks = []
for child in root:
    # print(child.tag, child.attrib)
    linksNodes = child.tag
    if (linksNodes=="links"):
        for childchild in child:
            # print(childchild.tag, childchild.attrib)
            links = childchild.tag
            if (links=="link"):
                attribs = childchild.attrib
                # print(attribs["id"])
                allLinks.append(attribs["id"])
# parameters
tripType = ['"' + "home" + '"', '"' + "work" + '"']
tripMode = ['"' + "car" + '"']

# give time
timeStr = 25200
timeEnd = 61200
cnt = 0

outfile = open("MATSim\streets_sdot_fixed_ToMATSim_randomPlan.xml", 'w')
# header
outfile.write('<?xml version="1.0" encoding="UTF-8"?>')
outfile.write('<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n')
outfile.write("<plans>\n")

for ix in range(timeStr, timeEnd):
    yesOrNot = random.randint(1, 1000)

    if (cnt==30): break

    if (yesOrNot % 2==0):
        # randomly assign trips
        randFrom = random.randint(0, len(allLinks))
        randTo = random.randint(0, len(allLinks))

        # assign links
        fromLink = '"' + str(allLinks[randFrom]) + '"'
        toLink = '"' + str(allLinks[randTo]) + '"'

        # assign departTime
        departTimeRaw = float(ix)
        departTime = '"' + str(time.strftime('%H:%M:%S', time.gmtime(departTimeRaw))) + '"'
        departTime_work = departTimeRaw + 4*3600
        departTime_work = '"' + str(time.strftime('%H:%M:%S', time.gmtime(departTime_work))) + '"'

        # assign ID
        id = '"' + str(cnt) + '"'

        # write data
        outfile.write("\t<person id=%s>\n" % id)
        outfile.write("\t\t<plan>\n")
        # activities: home
        outfile.write("\t\t\t<act type=%s link=%s end_time=%s />\n" % (tripType[0], fromLink, departTime))
        outfile.write("\t\t\t<leg mode=%s>\n" % tripMode[0])
        outfile.write("\t\t\t\t<route> </route>\n")
        outfile.write("\t\t\t</leg>\n")
        # activities: work
        outfile.write("\t\t\t<act type=%s link=%s end_time=%s />\n" % (tripType[1], toLink, departTime_work))
        outfile.write("\t\t\t<leg mode=%s>\n" % tripMode[0])
        outfile.write("\t\t\t\t<route> </route>\n")
        outfile.write("\t\t\t</leg>\n")
        # activities: home
        outfile.write("\t\t\t<act type=%s link=%s/>\n" % (tripType[0], fromLink))
        # break

        outfile.write("\t\t</plan>\n")
        outfile.write("\t</person>\n")
        cnt = cnt + 1


outfile.write("</plans>\n")
outfile.close()
