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
# This script will print the program parameters for
# a Nord Electro 4 ne4p file
# as exported from
# Nord Sound Manager 6.86 build 734_12 [OSX Intel]
#

import argparse
import struct
import sys

# converts 0x00 -> 0x3f to -15.0 -> +15.0
def dbFromSevenBitValue(i):
    return int((i - 0x3f) * 15.0 / 0x3f)

#  pulls 7 bits out of two bytes, e.g. those with an x here:
# - - - -  - x x x  x x x x  - - - -
# offset is the number of unused bits in c1 (in this sample, offset is 5)
def sevenBitValueFromChars(c1,c2,offset):
    mask = 1
    for m in range(0,7-offset):
        mask = (mask << 1) + 1
    # print 'offset:{} mask:{}'.format(offset,mask)
    msb = ord(c1) & mask
    lsb = ord(c2) >> (9-offset)
    sbv = ((msb << (offset-1)) + lsb)
    return sbv

# creates a string with the program information
def dumpNE4P(d):

    # dump is the output string
    dump = ''

    ######## ORGAN ########

    # model
    i = ord(d[0x10])
    organ = ''
    if i==0x12:
        organ = 'B3'
    if i==0x13:
        organ = 'Farf'
    if i==0x14:
        organ = 'Vox'

    # 0x49: bit 4: vib/chorus ON
    i = ord(d[0x49])
    if i & 0x0a:
        vibState = 'On'
    else:
        vibState = 'Off'

    # 0x3c-0x3f: drawbars 1-8, 2 drawbars per byte, values 0-8
    # 0x40: drawbar 9 in high byte
    i = ord(d[0x3c])
    drawbar1 = i >> 4
    drawbar2 = i & 0xf
    i = ord(d[0x3d])
    drawbar3 = i >> 4
    drawbar4 = i & 0xf
    i = ord(d[0x3e])
    drawbar5 = i >> 4
    drawbar6 = i & 0xf
    i = ord(d[0x3f])
    drawbar7 = i >> 4
    drawbar8 = i & 0xf
    i = ord(d[0x40])
    drawbar9 = i >> 4

    # 0x40: vibrato/chorus on (b3) 0x00=off 0x01=v1 0x03=c1 0x05=v2
    i = ord(d[0x40]) >> 1
    i = i & 0x7
    vibType = ''
    if i==0:
        vibType = 'V1'
    if i==1:
        vibType = 'C1'
    if i==2:
        vibType = 'V2'
    if i==3:
        vibType = 'C2'
    if i==4:
        vibType = 'V3'
    if i==5:
        vibType = 'C3'

    if organ:
        dump += 'Organ: {}  Vibrato/Chorus: {}  Type:{}  Drawbars: {}{}{}{}{}{}{}{}{}\n'.format(organ,vibState,vibType,\
                                                                                   drawbar1,drawbar2,drawbar3,\
                                                                                   drawbar4,drawbar5,drawbar6,\
                                                                                   drawbar7,drawbar8,drawbar9)

    ######## EFFECTS ########

    # 0x7b: bit 0: EQ ON
    i = ord(d[0x7b])
    if i & 0x80:
        eqState = 'On'
    else:
        eqState = 'Off'

    # 0x5f: EQ Bass Gain (7 bits)
    i = (ord(d[0x5f]) >> 1)
    eqBassGain = dbFromSevenBitValue(i)

    # 0x5f, 0x60: EQ Mid Freq 0=200 40=1000 7f=8K
    # this linear scale might not be right
    i = sevenBitValueFromChars(d[0x5d],d[0x60],7)
    if i<0x40:
        f = 800.0 * i / 0x3f
        f += 200
    else:
        i -= 0x40
        f = 7000.0 * i / 0x3f
        f += 1000
    eqMidFreq = int(round(f / 10) * 10)

    # 0x60, 0x61: EQ Mid Gain
    i = sevenBitValueFromChars(d[0x60],d[0x61],6)
    eqMidGain = dbFromSevenBitValue(i)

    # 0x61, 0x62: EQ Treble Gain (7 bits)
    i = sevenBitValueFromChars(d[0x61],d[0x62],5)
    eqTrebleGain = dbFromSevenBitValue(i)

    dump += 'EQ: {}  Bass:{:+} dB  Mid:{:+} dB ({} Hz)  Treble:{:+} dB\n'.format(eqState,eqBassGain,eqMidGain,eqMidFreq,eqTrebleGain)

    # 0x67, 0x68: Program Gain (7 bits)
    i = sevenBitValueFromChars(d[0x67],d[0x68],6)
    programGain = 10. * i / 0x7e
    dump += 'Program Gain: {}\n'.format(round(programGain,1))

    # 0x7b bit 1: efx1 on
    i = ord(d[0x7b])
    if i & 0x40:
        efx1State = 'On'
    else:
        efx1State = 'Off'

    # 0x62, 0x63: EFX1 gain (7 bits) offset 4
    i = sevenBitValueFromChars(d[0x62],d[0x63],4)
    rate = 10. * i / 0x7f
    dump += 'Effect 1: {}  Rate: {}\n'.format(efx1State,round(rate,1))

    # 0x7b bit 2: efx2 on
    i = ord(d[0x7b])
    if i & 0x20:
        efx2State = 'On'
    else:
        efx2State = 'Off'

    # 0x63, 0x64: EFX2 gain (7 bits) offset 7
    i = sevenBitValueFromChars(d[0x63],d[0x64],7)
    rate = 10. * i / 0x7f
    dump += 'Effect 2: {}  Rate: {}\n'.format(efx2State,round(rate,1))

    # 0x7b bit 3: spkr on
    i = ord(d[0x7b])
    if i & 0x10:
        speakerState = 'On'
    else:
        speakerState = 'Off'

    # 0x65, 0x66: Speaker Drive/Comp  (7 bits) offset 2
    i = sevenBitValueFromChars(d[0x65],d[0x66],2)
    rate = 10. * i / 0x7f
    dump += 'Speaker: {}  Drive/Comp: {}\n'.format(speakerState,round(rate,1))

    # 0x7b bit 4: delay/reverb on
    i = ord(d[0x7b])
    if i & 0x08:
        reverbState = 'On'
    else:
        reverbState = 'Off'

    # 0x66, 0x67: Delay/Reverb Mix (7 bits) offset 4
    i = sevenBitValueFromChars(d[0x66],d[0x67],4)
    rate = 10. * i / 0x7f
    dump += 'Delay/Reverb: {}  Mix: {}\n'.format(reverbState,round(rate,1))

    return dump


# main

parser = argparse.ArgumentParser(description='Dumps the program settings contained in Nord Electro 4 .ne4p files.')
parser.add_argument('inputFile', type=argparse.FileType('rb'), nargs='+', help='input Nord Sound Manager ne4p file(s)') # read binary files
args = parser.parse_args()

for f in args.inputFile:
    d = f.read()
    if d[:4] != 'CBIN' and d[9:13] != 'ne4p':
        print 'This does not appear to be a Nord NE4P file'
        continue
    else:
        print(f.name)
        print(dumpNE4P(d))
