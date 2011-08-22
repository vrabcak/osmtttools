# -*- coding: utf-8 -*-

__author__="vrabcak"
__date__ ="$24.7.2010 7:35:40$"


import xml.etree.cElementTree
import codecs



class Station :
    def __init__(self, name="", uic_ref=""):
        self.name=name
        self.uic_ref=uic_ref
        self.OSMref=[]

class OSMStation :
    def __init__(self, id=0, name="", uic_ref="" ):
        self.id=id
        self.name=name
        self.uic_ref=""
        self.matched = False

class StationList :
    """base class which handles both OSM and UIC station list"""
    def __init__(self):
        self.OSMstlist=[]
        self.UICstlist=[]
        self.max_OSM_nodes_for_station=0
        self.OSM_station_count=0
        
    def saveNode(self,node):

        id = node.attrib['id']
        name = ''
        for tag in node.findall('tag'):
            if tag.attrib['k'] == 'name':
                name = tag.attrib['v']
        self.OSMstlist.append( OSMStation(id,name) )
        self.OSM_station_count+=1
        print '*',
        if self.OSM_station_count%50 == 0 :
            print self.OSM_station_count

    def loadOSM(self,osmfile):
        print("Parsing OSM file...")
        document = iter(xml.etree.cElementTree.iterparse(osmfile))
        for ( _,elem) in document:
            if elem.tag == 'node':
                for tag in elem.findall('tag'):
                    if tag.attrib['k'] == 'railway' and ( tag.attrib['v'] == 'halt' or tag.attrib['v'] == 'station'):
                        self.saveNode(elem)
                elem.clear()
            elif elem.tag != 'tag':
                elem.clear()                
        print("Parsed.")
        self.OSMstlist.sort(key=lambda station:station.name)
        
    
    def  parseCSVFileLine(self,line):
        fields = line.split(';')
        if (len(fields) == 2) :
            uic_id = fields[0]
            name = fields[1].strip()
            if name.find('státní hranice') == -1:
                self.UICstlist.append(Station(name,uic_id))
        self.UICstlist.sort(key=lambda station:station.name)

    def loadCSV(self,csvfile):
        f = open(csvfile)
        for line in f :
            self.parseCSVFileLine(unicode(line,'cp1250'));

    def recordsCount(self):
        return len( self.OSMstlist ), len( self.UICstlist )

    def compareName(self, station, osm_station ):
        #print station.name,osm_station.name
        if( station.name == osm_station.name.strip() ):
            return True
        else:
            return False

    def countMaxOSMNodesForStation(self):
        """ Counts maximum number of osm nodes connected to one station """
        for st in self.UICstlist:
            if self.max_OSM_nodes_for_station < len(st.OSMref) :
                self.max_OSM_nodes_for_station = len(st.OSMref)

    def findMatches(self):
        self.matched_count = 0
        for st in self.UICstlist:
            for osmst in self.OSMstlist:
                if( self.compareName(st, osmst)):
                    self.matched_count+=1
                    st.OSMref.append(osmst)
                    osmst.matched = True
        self.countMaxOSMNodesForStation()

    def printOSMStList(self):
        for st in self.OSMstlist:
            print (st.id, repr(st.name))
        
    def printMatched(self):
        print ("Matched %d stations" % self.matched_count)
        for st in self.UICstlist:
            if len(st.OSMref) > 0:
                print (repr(st.name))
                
    def writeMatched(self):
        self.wikifile.write('== Seznam stanic a zastávek ==\n\n')
        self.wikifile.write('{| class="wikitable"\n')     
        for station in self.UICstlist:
            self.wikifile.write('|-\n')
            self.wikifile.write('|%s\n' % station.uic_ref )
            self.wikifile.write('|%s\n' % station.name )
            if ( len(station.OSMref) > 0 ):
                for i in range(0,len(station.OSMref)):
                    self.wikifile.write('|{{node|%s}}\n' % station.OSMref[i].id )
            else:
                self.wikifile.write('|\n') 
            self.wikifile.write('\n')
        self.wikifile.write('|}\n\n')
        
    def writeOrphanedOSM(self):
        self.wikifile.write('== Nespárované stanice v OSM ==\n\n')
        self.wikifile.write('{| class="wikitable"\n')      
        for station in sorted(self.OSMstlist, key = lambda st: st.name):
            if (not station.matched):
                self.wikifile.write('|-\n')
                self.wikifile.write('|%s\n' % station.name )
                self.wikifile.write('|{{node|%s}}\n' % station.id )
                self.wikifile.write('|[http://127.0.0.1:8111/import?url=http://api.openstreetmap.org/api/0.6/node/%s josm]\n' % station.id )
                self.wikifile.write('\n')   
        self.wikifile.write('|}\n\n')
    
    def writeWiki(self):
        self.wikifile = codecs.open('../out/wiki.wiki',mode='w', encoding='utf-8' )
        self.writeMatched()
        self.writeOrphanedOSM()
             
           

########################### main #################################
if __name__ == "__main__":

    #settings
    CSVFILE="../res/stanice.csv"
    OSMFILE="../res/czech_republic.osm"
    
    #main
    stlist=StationList()
    stlist.loadCSV(CSVFILE)
    stlist.loadOSM(OSMFILE)
    print "Loaded ",stlist.recordsCount(),"records."

    
    #stlist.printOSMStList();


    print "Finding matches"
    stlist.findMatches()
    print "Done."
    stlist.writeWiki()
    