# -*- coding: utf-8 -*-
# Python script for extraction of style metadata to JSON
# Author: Rintze M. Zelle
# Version: 2014-05-25
# * Requires lxml library (http://lxml.de/)

import os, glob, re, inspect, json
from lxml import etree

# http://stackoverflow.com/questions/50499
folderPath =  os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

parentFolderPath = os.path.dirname (folderPath)
path =  os.path.join(parentFolderPath, 'styles')

stylesMetadata = []
styles = []

for stylepath in glob.glob( os.path.join(path, '*.csl') ):
    styles.append(os.path.join(stylepath))
for stylepath in glob.glob( os.path.join(path, 'dependent', '*.csl') ):
    styles.append(os.path.join(stylepath))

for style in styles:
    styleMetadata = []

    parser = etree.XMLParser(remove_blank_text=True)
    parsedStyle = etree.parse(style, parser)
    styleElement = parsedStyle.getroot()

    if "default-locale" in styleElement.attrib:
        defaultLocale = styleElement.get("default-locale")
    else:
        defaultLocale = ""

    csInfo = styleElement.find(".//{http://purl.org/net/xbiblio/csl}info")

    try:
        title = csInfo.find(".//{http://purl.org/net/xbiblio/csl}title").text
    except:
        title = ""
        pass

    try:
        parent = csInfo.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='independent-parent']").get("href")
        parent = parent.split("/styles/")[1]
    except:
        parent = ""
        pass

    try:
        documentation = csInfo.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='documentation']").get("href")
    except:
        documentation = ""
        pass

    try:
        citationFormat = csInfo.find(".//{http://purl.org/net/xbiblio/csl}category[@citation-format]").get("citation-format")
    except:
        citationFormat = ""
        pass

    try:
        fieldElements = csInfo.findall(".//{http://purl.org/net/xbiblio/csl}category[@field]")
        fieldsList = []
        for field in fieldElements:
            fieldsList.append(field.get("field"))
        fields = ";".join(fieldsList)
    except:
        fields = ""
        pass

    try:
        issn = csInfo.find(".//{http://purl.org/net/xbiblio/csl}issn").text
    except:
        issn = ""
        pass

    try:
        eissn = csInfo.find(".//{http://purl.org/net/xbiblio/csl}eissn").text
    except:
        eissn = ""
        pass

    try:
        comment = parsedStyle.xpath("/cs:style/comment()", namespaces={"cs": "http://purl.org/net/xbiblio/csl"})[0]
        metadataSet = comment.text.split("generate_dependent_styles/data/")[1].strip()
    except:
        metadataSet = ""
        pass

    styleID = os.path.basename(style).split(".csl")[0]

    styleMetadata.append(title) #0
    styleMetadata.append(styleID) #1
    styleMetadata.append(defaultLocale) #2
    styleMetadata.append(parent) #3
    styleMetadata.append(metadataSet) #4
    styleMetadata.append(citationFormat) #5
    styleMetadata.append(fields) #6
    styleMetadata.append(issn) #7
    styleMetadata.append(eissn) #8
    styleMetadata.append(documentation) #9

    stylesMetadata.append(styleMetadata)

outputDict = {'data': stylesMetadata}

with open('style-metadata.json', 'w') as file:
    json.dump(outputDict, file)

# Limit ourselves to non-generated styles
parents = {}
for i in outputDict['data']:
    if i[3] != "" and i[4] == "":
        if i[3] in parents:
            parents[i[3]].append(i[0])
        else:
            parents[i[3]] = [i[0]]

with open('style-parent.json', 'w') as file:
    json.dump(parents, file)

parentCount = {}
for i in parents:
    parentCount[i] = len(parents[i])

sortedParents = sorted(parentCount, key=parentCount.get, reverse=True)

parentOutput = ""
for i in sortedParents:
    parentOutput += i + ": " + str(parentCount[i]) + "\n"

f = open('style-parent-count.txt', 'w')
f.write ( parentOutput )
f.close()

# Count of auto-generated styles
metadataSets = {}
for i in outputDict['data']:
    if i[4] != "":
        if i[4] in metadataSets:
            metadataSets[i[4]].append(i[0])
        else:
            metadataSets[i[4]] = [i[0]]

# Rename metadata sets
publishersPath =  os.path.join(parentFolderPath, 'utilities', 'generate_dependent_styles', 'data', 'publishers.json')
with open(publishersPath) as publisherNamesJSON:
    publisherNames = json.load(publisherNamesJSON)

for i in publisherNames:
    if i in metadataSets:
        metadataSets[publisherNames[i]] = metadataSets.pop(i)

metadataSetsCount = {}
for i in metadataSets:
    metadataSetsCount[i] = len(metadataSets[i])

sortedMetadataSets = sorted(metadataSetsCount, key=metadataSetsCount.get, reverse=True)

metadataSetsOutput = ""
totalGeneratedStyles = 0
for i in sortedMetadataSets:
    metadataSetsOutput += i + ": " + str(metadataSetsCount[i]) + "\n"
    totalGeneratedStyles += metadataSetsCount[i]

metadataSetsOutput = "Total: " + str(totalGeneratedStyles) + "\n===\n" + metadataSetsOutput

f = open('style-metadatasets-count.txt', 'w')
f.write ( metadataSetsOutput )
f.close()

# Extract Metadata
extractedMetadata = "Title\tISSN\teISSN\tDocumentation\tField\n"
for i in outputDict['data']:
    if i[3] == "proceedings-of-the-royal-society-b":
        extractedMetadata += i[0] + "\t" + i[7] + "\t" + i[8] + "\t" + i[9] + "\t" + i[6] + "\n"

f = open('extracted-metadata.txt', 'w')
f.write ( extractedMetadata )
f.close()

eissnList = [
        "1745-7254",
        "1572-0241",
        "1948-9501",
        "2044-5385",
        "1476-5365",
        "1476-5373",
        "1532-1827",
        "1476-5500",
        "1476-5403",
        "2041-4889",
        "1748-7838",
        "2042-0226",
        "2050-0068",
        "2155-384X",
        "1532-6535",
        "2163-8306",
        "2222-1751",
        "1476-5640",
        "1476-5438",
        "1476-5446",
        "2092-6413",
        "1476-5454",
        "1476-5462",
        "1476-5470",
        "1530-0366",
        "1365-2540",
        "2052-7276",
        "1348-4214",
        "1940-8692",
        "1440-1711",
        "1476-5489",
        "1476-5497",
        "2046-2174",
        "2049-3169",
        "1559-7016",
        "1559-064X",
        "1435-232X",
        "1476-5527",
        "1523-1747",
        "1529-1774",
        "1476-5543",
        "1523-1755",
        "2157-1716",
        "1548-4475",
        "1530-0307",
        "1476-5551",
        "2044-5229",
        "2047-7538",
        "1530-0285",
        "1476-5578",
        "1744-4292",
        "1525-0024",
        "2162-2531",
        "1935-3456",
        "1546-1696",
        "1476-4679",
        "1552-4469",
        "1755-4349",
        "1758-6798",
        "2041-1723",
        "1546-1718",
        "1752-0908",
        "1529-2916",
        "1476-4660",
        "1546-170X",
        "1548-7105",
        "1748-3395",
        "1546-1726",
        "1749-4893",
        "1745-2481",
        "1750-2799",
        "1474-1768",
        "1759-5010",
        "1759-4782",
        "1474-1784",
        "1759-5037",
        "1759-5053",
        "1471-0064",
        "1474-1741",
        "1740-1534",
        "1471-0080",
        "1759-507X",
        "1759-4766",
        "1471-0048",
        "1759-4804",
        "1759-4820",
        "1545-9985",
        "1470-634X",
        "1884-4057",
        "2044-4052",
        "1476-5594",
        "2157-9024",
        "1530-0447",
        "1349-0540",
        "1476-5608",
        "1945-3477",
        "0036-8733",
        "1555-2284",
        "2045-2322",
        "1476-5624",
        "1751-7370",
        "1881-1469",
        "1473-1150",
        "2158-3188",
        "1471-7511"]

for i in outputDict['data']:
    if i[8] in eissnList:
        print(i[8] + "\t" + i[1] + "\t" + i[3])
