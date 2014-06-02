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

