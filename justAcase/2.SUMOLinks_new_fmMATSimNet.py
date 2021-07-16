import xml.etree.ElementTree as ET
import json

folder = "MATSim/"
outputFolder = "MATSim/"
tree = ET.parse(folder + "/" + "streets_sdot_fixed_ToMATSim_DowntownLinks.xml")
root = tree.getroot()

SUMOLinks = []
for child in root:
    print(child.tag, child.attrib)
    linksNodes = child.tag
    if (linksNodes=="links"):
        for childchild in child:
            # print(childchild.tag, childchild.attrib)
            links = childchild.tag
            if (links=="link"):
                attribs = childchild.attrib
                print(attribs["id"])
                SUMOLinks.append(attribs["id"])

with open(outputFolder + 'SUMOLinks.txt', 'w') as f:
    for link in SUMOLinks:
        f.write("%s\n" % link)
