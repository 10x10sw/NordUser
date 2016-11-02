#
# MIT License
# 
# Copyright (c) 2016 Christian-E! / Ten by Ten Software
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

#
# This script will convert the program list for 
#       Nord Electro 4
#       Nord Stage 2/2EX 
# as exported from 
# Nord Sound Manager 6.86 build 734_12 [OSX Intel]
# into a grid-style bank and program table.
#

import sys
import argparse
from xml.etree import ElementTree

parser = argparse.ArgumentParser(description='Creates a Program Reference Card for Nord Keyboards.')
parser.add_argument('-v', '--verbose', action='store_const', const=1, default=0, help='print the sample name or organ category below the program name')
parser.add_argument('-r', '--reverse', action='store_const', const=1, default=0, help='print the program pages in reverse order (from high to low)')
parser.add_argument('inputFile', type=str, help='the input Nord Electro 4 Program HTML file')
parser.add_argument('-o', '--outputFile', type=str, help='the output HTML file')
parser.add_argument('-t', '--title', type=str, help='an optional title to print above each bank')
parser.add_argument('--eurostile', action='store_const', const=1, default=0, help='use Eurostile Extd font for titles')
args = parser.parse_args()
# print args

xml = ''

# read the input HTML 
filename = args.inputFile
f = open(filename) 
html = f.read()

# reduce the HTML to just the table
tableBegin = html.find('<table>')
tableEnd = html.find('</table>',tableBegin)
html = html[tableBegin:tableEnd+8]

# remove unquoted styling
html = html.replace(' class=odd','')

# fix the header lines; they end in </td> instead of </th>
lfixth = html.rsplit('<th>')
for line in lfixth:
    tdIndex = line.find('</td>\n');
    if tdIndex == -1:
        xml += line
    else:
        if tdIndex == len(line)-6:
            xml += '<th>' + line.rstrip('</td>\n') + '</th>'
        else:
            xml += '<th>' + line[:tdIndex] + '</th>' + line[tdIndex+6:]

# parse the table 
table = ElementTree.XML(xml)
rows = iter(table)
numCols = len(next(rows))
# headers = [col.text for col in next(rows)]

# ----- Electro 4 -----
# 32 pages of 4 programs
# table data:8 columns 
# 2:location (page:program)
# 3:name
# 4:category
# 6:sample
if numCols == 8:
    numPages = 32
    numBanks = 1
    numPrograms = 4

# ----- Stage 2 -----
# 2 banks with 20 pages of 5 programs
# table data:11 columns
# 1:bank 
# 2:location (page:program)
# 3:name
# 4:category
# 6:piano A
# 7:sample A
# 8:piano B
# 9:sample B
if numCols == 11:
    numPages = 20
    numBanks = 4
    numPrograms = 5

# function to values based on bank and location
def findValues(table, bankName, location):
    rows = iter(table)
    for row in rows:
        values = [col.text for col in row]
        for value in values:
            if value == location:
                if values[1] == bankName:
                    return values;

#for row in rows:
#    values = [col.text for col in row]
#    print dict(zip(headers, values))

# build new html
html = '<html>\n'
html += '<head><style>\n\
body, table {font:normal 6pt Trebuchet, Trebuchet MS, Helvetica Neue, Helvetica, Arial, sans-serif;}\n\
.bank {padding:6pt; background:black; overflow:hidden; border:1pt solid gray; -webkit-border-radius:10pt; -moz-border-radius:10pt; border-radius:10pt;}\n\
h1,h2 {text-align:center; text-transform:uppercase;}\n\
h2 {color:white;}\n\
.programs {background:white; border:1pt solid gray; -webkit-border-radius:5pt; -moz-border-radius:5pt; border-radius:5pt;}\n\
.name {font-weight:bold; font-size: 140%; display:inline;}\n\
.catsamp {display:inline;}\n\
.break {page-break-before:always; background:white; xpadding:10pt;}\n\
table {border-collapse:collapse; width:100%;}\n\
table tbody td {color:black; border-bottom:1pt solid lightgray;}\n'
html += 'table tbody td.location {{font-size:120%; font-weight:bold; padding:2pt; text-align:center; border-left:1pt solid lightgray; width:{}%;}}\n'.format(20/numPrograms)
html += 'table tbody td.info {{padding:2pt; width:{}%;}}\n'.format(80/numPrograms)
html += 'table tbody td:first-child {border-left:none;}\n\
table tbody tr:last-child td {border-bottom:none;}\n'
if args.eurostile:
    html += 'h1,h2 {font:bold 14pt Eurostile Extd, Helvetica Neue, Helvetica, Arial, sans-serif; margin:0}'
    html += '.location {font-family:Eurostile}'
else: 
    html += 'h1,h2 {font:bold 12pt Helvetica Neue, Helvetica, Arial, sans-serif; margin:0pt 0pt 6pt 0pt; -webkit-transform:scale(2,1); -moz-transform:scale(2,1); -ms-transform:scale(2,1); transform:scale(2,1);}\n'

html += '</style></head>\n'

html += '<body>\n'

for bank in range(0,numBanks):

    if args.title:
        html += '<h1>' + args.title + '</h1>\n';

    html += '<div class="bank">'

    if numBanks>1:
        bankName = 'Bank {:X}'.format(0xA+bank)
        html += '<h2>' + bankName + '</h2>\n'
    else:
        bankName = 'Program'

    html += '<div class="programs"><table>\n'

    for p in range(0,numPages):

        page = p+1
        if args.reverse:
            page = numPages-p

        html += '<tr>'
        for program in range(1,numPrograms+1):
            location = '{:02d}:{}'.format(page,program)

            name = ''
            samp = ''
            cat = ''

            values = findValues(table,bankName,location)

            if values:
                name = values[3]
                cat = values[4]
                if numCols == 8:# Electro 4
                    samp = values[6]
                if numCols == 11:# Stage 2
                    samp = values[6] + '<br>' + values[7] + '<br>' + values[8] + '<br>' + values[9] 

            html += '<td class="location">' + location + '</td><td class="info"><div class="name">' + name

            # for organs, show the model. otherwise, show the sample name
            if args.verbose:
                if cat == 'B3' or cat == 'Farf' or cat == 'Vx':
                    html += '</div><br><div class="catsamp">' + cat + '</div></td>'
                else:
                    html += '</div><br><div class="catsamp">' + samp + '</div></td>'

            html += '</div></td>'

        html += '</tr>\n'

    html += '</table></div></div>' # programs and bank divs

    if bank < numBanks-1:
        html += '<div class="break"></div>'

html += '</div></body></html>'

# optionally write directly to a file
if args.outputFile:
    outHtmlFile = open(args.outputFile, 'w')
    outHtmlFile.write(html)
else:
    print html

# This was my first Python script. Thanks for watching!
