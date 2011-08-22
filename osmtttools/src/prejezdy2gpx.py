# -*- coding: cp1250 -*-
# zkonveruje seznam prejezdu od SZDC do GPX
import re

# settings
crossings_file = '../res/seznamPrejezdu.csv'
gpx_1 = '../out/prejezdy1.gpx'
gpx_2 = '../out/prejezdy2.gpx'
gpx_3 = '../out/prejezdy3.gpx'
gpx_U = '../out/prejezdyU.gpx'
gpx_MK = '../out/prejezdyMK.gpx'
gpx_other = '../out/prejezdyOTH.gpx'


class crossingInfo :
    def convertCoord(self,coord):
        m = re.match("([0-9]+)°(.+)'(.+)''", coord)
        if (m): 
            deg = float(m.group(1))
            minute = float(m.group(2))
            sec   = float(m.group(3)) 
            decimalcoord = deg + minute/60 + sec/3600
            return decimalcoord
        else:
            return 0.0
        
    def parseLine(self,line):
        fields = line.split(';')
        self.id = fields[0]
        self.track = fields[1]
        self.highwaytype = fields[2]
        self.lat = self.convertCoord(fields[3])
        self.lon = self.convertCoord(fields[4])
        
class gpxWriter:
    def __init__ (self,filename):
        self.file = open(filename,'w');
        self.file.write('<?xml version="1.0"?>\n')
        self.file.write('<gpx version="1.0" \
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
        xmlns="http://www.topografix.com/GPX/1/0" \
        xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n')
        
    def waypoint(self, lat, lon, name):
        self.file.write('<wpt lat="%f" lon="%f"> \n' % (cross.lat, cross.lon))
        self.file.write('<name>%s</name> \n' % name)
        self.file.write('</wpt> \n')
        
    def __del__(self):
        self.file.write('</gpx>')
        self.file.flush()
        
        
# main
csvfile = open(crossings_file)
jednicky = gpxWriter(gpx_1)
dvojky = gpxWriter(gpx_2)
trojky = gpxWriter(gpx_3)
ucelovky = gpxWriter(gpx_U)
mistni = gpxWriter(gpx_MK)
jine = gpxWriter(gpx_other)

for line in csvfile:    
    cross = crossingInfo()
    cross.parseLine(line)
    if (cross.lat != 0 and cross.lon != 0):
        if (cross.highwaytype == "I."):
            jednicky.waypoint(cross.lat,cross.lon,cross.id+' '+cross.track+' '+cross.highwaytype)
        elif (cross.highwaytype == "II."):
            dvojky.waypoint(cross.lat,cross.lon,cross.id+' '+cross.track+' '+cross.highwaytype)
        elif (cross.highwaytype == "III."):
            trojky.waypoint(cross.lat,cross.lon,cross.id+' '+cross.track+' '+cross.highwaytype)
        elif (cross.highwaytype == "U"):
            ucelovky.waypoint(cross.lat,cross.lon,cross.id+' '+cross.track+' '+cross.highwaytype)
        elif (cross.highwaytype == "MK"):
            mistni.waypoint(cross.lat,cross.lon,cross.id+' '+cross.track+' '+cross.highwaytype)
        else:
            jine.waypoint(cross.lat,cross.lon,cross.id+' '+cross.track+' '+cross.highwaytype)
            
print "Finished."

    
    
