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

for stylepath in glob.glob( os.path.join(path, 'z*.csl') ):
    styles.append(os.path.join(stylepath))
#for stylepath in glob.glob( os.path.join(path, 'dependent', '*.csl') ):
#    styles.append(os.path.join(stylepath))

# title, id, default-locale, citation-format (1), categories, parent, id, issn, eissn, generated

# os.path.basename(style)

#                "link[@independent-parent]", "link[@template]",
#                "link[@documentation]", "author", "contributor",
#                "category[@citation-format]", "category[@field]", "issn",
#                "eissn", "issnl", "summary", "published", "updated", "rights",
#                "end-comment"]

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

    styleID = os.path.basename(style).split(".csl")[0]

    styleMetadata.append(title)
    styleMetadata.append(styleID)
    styleMetadata.append(defaultLocale)

    stylesMetadata.append(styleMetadata)

    outputDict = {'data': stylesMetadata};

with open('style-metadata.json', 'w') as file:
    json.dump(outputDict, file)
