#
# This script will convert the Nord Electro 4D Program List
# as exported from 
# Nord Sound Manager 6.86 build 734_12 [OSX Intel]
# into a grid-style bank and program table.
#
# (c) 2016 Christian-E! / Ten by Ten Software
#

import sys
import argparse
from xml.etree import ElementTree

parser = argparse.ArgumentParser(description='Creates a Nord Electro 4 Program Reference Card in HTML.')
parser.add_argument('-s', '--showSample', action='store_const', const=1, default=0, help='print the sample name or organ category below the program name')
parser.add_argument('-r', '--reverse', action='store_const', const=1, default=0, help='print the programs in reverse order (from 1 to 32)')
parser.add_argument('inputFile', type=str, help='the input Nord Electro 4 Program HTML file')
parser.add_argument('-o', '--outputFile', type=str, help='the output HTML file')
args = parser.parse_args()
# print args

xml = ""

# read the input HTML 
filename = args.inputFile
f = open(filename) 
html = f.read()

# reduce the HTML to just the table
tableBegin = html.find("<table>")
tableEnd = html.find("</table>",tableBegin)
html = html[tableBegin:tableEnd+8]

# remove unquoted styling
html = html.replace(" class=odd","")

# fix the header lines; they end in </td> instead of </th>
lfixth = html.rsplit("<th>")
for line in lfixth:
    tdIndex = line.find("</td>\n");
    if tdIndex == -1:
        xml += line
    else:
        if tdIndex == len(line)-6:
            xml += "<th>" + line.rstrip("</td>\n") + "</th>"
        else:
            xml += "<th>" + line[:tdIndex] + "</th>" + line[tdIndex+6:]

# parse the table 
table = ElementTree.XML(xml)

#rows = iter(table)
#headers = [col.text for col in next(rows)]
#for row in rows:
#    values = [col.text for col in row]
#    print dict(zip(headers, values))

# build new html
html = "<html>\n"
html += "<head><style>\n\
.electro {font: normal 12px/150% Helvetica Neue, Helvetica, Arial, sans-serif; background: white; overflow: hidden; border: 1px solid gray; -webkit-border-radius: 5px; -moz-border-radius: 5px; border-radius: 5px; }\n\
.name {font: bold 12px/100% Helvetica Neue, Helvetica, Arial, sans-serif; display:inline; }\n\
.catsamp {font: normal 10px Helvetica Neue, Helvetica, Arial, sans-serif; display:inline; }\n\
table {border-collapse: collapse; text-align: left; width: 100%; }\n\
table td, table th { padding: 3px 10px; }\n\
table tbody td {color: black; font-size: 12px; border-bottom: 1px solid lightgray; }\n\
table tbody td.address { padding: 3px 0px 3px 10px; border-left: 1px solid lightgray; }\n\
table tbody td.info { padding: 3px 3px; }\n\
table tbody td:first-child { border-left: none; }\n\
table tbody tr:last-child td { border-bottom: none; }\n\
</style></head>\n"

html += "<body><div class='electro'><table>\n"

for b in range(1,33):

    bank = 33-b
    if args.reverse:
        bank = b

    html += "<tr>"
    for p in range(1,5):
        address = "{:02d}:{}".format(bank,p)

        name = ""
        samp = ""
        cat = ""

        rows = iter(table)
        for row in rows:
            values = [col.text for col in row]
            for value in values:
                if value == address:
                    name = values[3]
                    cat = values[4]
                    samp = values[6]

        html += "<td class='address'>" + address + "</td><td class='info'><div class='name'>" + name

        # for organs, show the model. otherwise, show the sample name
        if args.showSample:
            if cat == "B3" or cat == "Farf" or cat == "Vx":
                html += "</div><br><div class='catsamp'>" + cat + "</div></td>"
            else:
                html += "</div><br><div class='catsamp'>" + samp + "</div></td>"

        html += "</div></td>"

    html += "</tr>\n"

html += "</table></div></body></html>"

# optionally write directly to a file
if args.outputFile:
    outHtmlFile = open(args.outputFile, 'w')
    outHtmlFile.write(html)
else:
    print html

# This was my first Python script. Thanks for watching!
