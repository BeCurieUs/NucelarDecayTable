import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import collections
import json

urlfilter = "nuclide.asp?iZA"
baseurl="http://nucleardata.nuclear.lu.se/toi/listnuc.asp?"
rooturl="http://nucleardata.nuclear.lu.se/toi/"
allisotopes = []
isotopeproperties=[]
jsonToExport = []

#Range sets the range of values to extract based on atomic mass
#the ranges are fed into some urls to extract all url pages for individual isotope data
for atomicweight in range(1,12):
    addedurl=baseurl+"sql=&A1="+str(atomicweight)+"&A2="+str(atomicweight)
    html = urllib.request.urlopen(addedurl).read()
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('a')
    # each atomic mass might have several isotopes, have to iterate through
    for link in tags:
        # Grab only the corrent links, not links to the outside
        if link.get('href').startswith("nuclide.asp?iZA"):
            allisotopes.append(rooturl+link.get('href'))




for isotopes in allisotopes:
    openpageisotope = urllib.request.urlopen(isotopes).read()
    doublethesoup=BeautifulSoup(openpageisotope,'html.parser')

    nametag = doublethesoup.find('th',{"rowspan": '2'})
    elementsymbol=nametag.get_text()
    #magic set of parameters that find us the unique tags used to make
    #the name. Name is also part of the weight table, this tag used to derive the rest
    #which don't have unique ways to inditify them

    weightandnametrtag=nametag.parent
    #Row with both weight and name

    atomicweight=weightandnametrtag.th.get_text()
    #get dat weight!

    weightnametable=weightandnametrtag.parent
    #table containing the already captured atomic weight and name in the first row
    #and uncaptured neutron and proton number in the second row
    neutronandprotontag=weightnametable.find_all('tr')
    #get all rows now
    neutronandprotontag=neutronandprotontag[1]
    #we want the second TR tag in the table, first is already captured
    neutronandprotonlistoftags=neutronandprotontag.find_all('th')
    #then break it down to its 2 componate tags we want

    neutronnumber = neutronandprotonlistoftags[1].get_text()
    protonnumber  = neutronandprotonlistoftags[0].get_text()
    #Nab each one in the array, make sure not to get it backwards like I did

    #this code is now only.....
    #    findalltr = doublethesoup.find_all('tr')
    #    for value in findalltr:
    #        if value.th:
    #
    #        if value.th.get_text().startswith("Half"):
    #            print("Half life     : " +value.td.get_text())
    #....This code bellow, oh god why did I make this so hard keeping as memorial to learning
    halflife = doublethesoup.find(text="Half life: ").find_next('td').get_text()

    #Sadly, we must now brute force
    decaypathtagitertor = ""
    #container for all our data
    decaylist=collections.OrderedDict()
    #It could have been just a regular dictionary, but everyone needs order in their life
    decaylist['Symbol']=elementsymbol+atomicweight
    decaylist['Halflife']=halflife
    #throw in the things we already know and are better inditifiers than the
    #upcoming decay modes and neutronandprotonlistoftags

    if doublethesoup.find(text="Decay properties:"):
        #truthy find of decay properies, if it fails is means it doesn't have decay properies
        decaypathtagitertor = doublethesoup.find(text="Decay properties:").find_next('td').parent
        #now this this won't fail, there are an unknown number of decay modes
        #that are all siblings of the next td tag.
        while True:
            if decaypathtagitertor.find('th'):
                #if we find a th tag, we have finally finished all decay modes
                break
            rows = decaypathtagitertor.find_all('td')
            #get decay mode and decay ratio
            mode = rows[0].get_text()
            branch = rows[1].get_text()
            #there are potentialy more elements to grab in the td's but we only grab first 2
            decaylist[mode]=branch
            #throw it in the big mega list
            decaypathtagitertor = decaypathtagitertor.find_next('tr')
            #move to the next sibling, potential failure mode here if there are other
            #ways the decay things terminate

        #while True:
            #if decaypathtagitertor.tr:
                #if
            #else:
                #continue
        #decaypathtagitertor =  decaypathtagitertor.find_next('tr')


    #print(decaylist)
    # for key,val in decaylist.items():
    #     print(key+" "+val)
    # print("")

    jsonToExport.append(json.dumps(decaylist))
    print(jsonToExport)