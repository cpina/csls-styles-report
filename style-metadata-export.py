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

    styleMetadata.append(title)
    styleMetadata.append(styleID)
    styleMetadata.append(defaultLocale)
    styleMetadata.append(parent)
    styleMetadata.append(metadataSet)
    styleMetadata.append(citationFormat)
    styleMetadata.append(fields)
    styleMetadata.append(issn)
    styleMetadata.append(eissn)

    stylesMetadata.append(styleMetadata)

    outputDict = {'data': stylesMetadata};

with open('style-metadata.json', 'w') as file:
    json.dump(outputDict, file)
