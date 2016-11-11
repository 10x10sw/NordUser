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

parser = argparse.ArgumentParser(description='Dumps the program settings contained in Nord Electro 4 .ne4p files.')
parser.add_argument('inputFile', type=str, help='the input Nord Sound Manager ne4p file')
args = parser.parse_args()
# print(args)

# read the input binary
d = open(args.inputFile, 'rb').read()

if d[:4] != 'CBIN' and d[9:13] != 'ne4p':
    print 'This does not appear to be a Nord NE4P file'
    exit

# function to convert 0x00 -> 0x3f to -15 -> +15
def dbFromSevenBitValue(i):
    return int((i - 0x3f) * 15.0 / 0x3f)

def sevenBitValueFromChars(c1,c2,offset):
    mask = 1
    for m in range(0,7-offset):
        mask = (mask << 1) + 1
    # print 'offset:{} mask:{}'.format(offset,mask)
    msb = ord(c1) & mask
    lsb = ord(c2) >> (9-offset)
    sbv = ((msb << (offset-1)) + lsb)
    return sbv


#ORGAN

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

# 0x40: vibrato/chorus on (b3) 0x00=off 0x01=v1 0x03=c1 0x05=v2

if organ:
    print 'Organ: {}  Vibrato/Chorus: {} '.format(organ,vibState)


# EFFECTS

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
# - - - -  - - - x  x x x x  x x - -
#msb = ord(d[0x5f]) & 0x1
#lsb = ord(d[0x60]) >> 2
#i = ((msb << 6) + lsb)
i = sevenBitValueFromChars(d[0x5d],d[0x60],7)
if i<0x40:
    f = 800.0 * i / 0x3f
    f += 200
else:
    i -= 0x40
    f = 7000.0 * i / 0x3f
    f += 1000
# print '{} {}'.format(i,f)
eqMidFreq = int(round(f / 10) * 10)

# 0x60, 0x61: EQ Mid Gain
# - - - -  - - x x  x x x x  x - - -
#msb = ord(d[0x60]) & 0x3
#lsb = ord(d[0x61]) >> 3
#i = ((msb << 5) + lsb)
i = sevenBitValueFromChars(d[0x60],d[0x61],6)
eqMidGain = dbFromSevenBitValue(i)

# 0x61, 0x62: EQ Treble Gain (7 bits)
# - - - -  - x x x  x x x x  - - - -
#msb = ord(d[0x61]) & 0x7
#lsb = ord(d[0x62]) >> 4
#i = ((msb << 4) + lsb)
i = sevenBitValueFromChars(d[0x61],d[0x62],5)
eqTrebleGain = dbFromSevenBitValue(i)

print 'EQ: {}  Bass:{:+} dB  Mid:{:+} dB ({} Hz)  Treble:{:+} dB'.format(eqState,eqBassGain,eqMidGain,eqMidFreq,eqTrebleGain)

# 0x67, 0x68: Program Gain (7 bits)
# - - - -  - - x x  x x x x  x - - -
#msb = ord(d[0x67]) & 0x3
#lsb = ord(d[0x68]) >> 3
#i = ((msb << 5) + lsb) << 1
i = sevenBitValueFromChars(d[0x67],d[0x68],6)
programGain = 10. * i / 0x7e
print 'Program Gain: {}'.format(round(programGain,1))

# 0x7b bit 1: efx1 on
i = ord(d[0x7b])
if i & 0x40:
    efx1State = 'On'
else:
    efx1State = 'Off'

# 0x62, 0x63: EFX1 gain (7 bits) offset 4
i = sevenBitValueFromChars(d[0x62],d[0x63],4)
rate = 10. * i / 0x7f
print 'Effect 1: {}  Rate: {}'.format(efx1State,round(rate,1))

# 0x7b bit 2: efx2 on
i = ord(d[0x7b])
if i & 0x20:
    efx2State = 'On'
else:
    efx2State = 'Off'

# 0x63, 0x64: EFX2 gain (7 bits) offset 7
i = sevenBitValueFromChars(d[0x63],d[0x64],7)
rate = 10. * i / 0x7f
print 'Effect 2: {}  Rate: {}'.format(efx2State,round(rate,1))

# 0x7b bit 3: spkr on
i = ord(d[0x7b])
if i & 0x10:
    speakerState = 'On'
else:
    speakerState = 'Off'

# 0x65, 0x66: Speaker Drive/Comp  (7 bits) offset 2
i = sevenBitValueFromChars(d[0x65],d[0x66],2)
rate = 10. * i / 0x7f
print 'Speaker: {}  Drive/Comp: {}'.format(speakerState,round(rate,1))

# 0x7b bit 4: delay/reverb on
i = ord(d[0x7b])
if i & 0x08:
    reverbState = 'On'
else:
    reverbState = 'Off'

# 0x66, 0x67: Delay/Reverb Mix (7 bits) offset 4
i = sevenBitValueFromChars(d[0x66],d[0x67],4)
rate = 10. * i / 0x7f
print 'Delay/Reverb: {}  Mix: {}'.format(reverbState,round(rate,1))
