print "========================================================================="
print "josm-to-potlatch2-preset-conversion.py"
print "original script written by Pierre Beland, 2011-03"
print "========================================================================="
"""
 parse XML from josm preset file with lxml iterparse method
 this XML parser permits to treat big files with minimal memory usage
 START tag events : create new JOSM_element
 END tag events : append tag / write files

 JOSM_presets : JOSM presets file (input)
 OUTPUT to potlatch2 preset main file
 potlatch2_preset : potlatch2 preset file (output)
 OUTPUT to potlatch2 group menu file
 potlatch2_group : potlatch2 group file (output) : creates a file for each first level of group tag
 
 Copyright (c) 2011 Pierre Beland
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
=========================================================================
"""

"""
=========================================================================
 CUSTOM PRESET : Conversion from JOSM to potlatch2
 humanitarian preset , test file
=========================================================================
"""

import os
from lxml import etree
os.chdir('f:\osm\potlach2\\')


josm_file='humanitarian_presets_josm.xml'

infile = open(josm_file, 'r')
print "NOTE : this script expects the JOSM preset file to contain two levels of GROUP Tags.\nThe second level will be used to save Potlatch2 preset categories.\n<group>\n\t<group>\n"
print "MISSING TAGS AND NODES NOT TREATED IN THE CONVERSION ROUTINE WILL\nBE REPORTED BELOW WITH ERROR MESSAGE INDICATION\n"
print "=========================================================================\n"
print "JOSM INPUT : file=",josm_file, "\n"

"""
=========================================================================
 FUNCTIONS : TAG conversion from JOSM to Potlatch2
=========================================================================
"""

def fPrintCurrentElement():
    global JOSM_element
    txt_element=etree.tostring(JOSM_element)
    colend=txt_element.find(">")+1
    if colend<2: colend=120
    print txt_element[0:colend], "\n***************************************"

def fPresetsStart ():
    global potlatch2_preset    
    # root tag
    potlatch2_preset=etree.Element("mapFeatures")
    comment = etree.Comment('  Conversion from JOSM to potlatch2 made with josm-to-potlatch2-preset-conversion.py\n\tPython script by Pierre Beland  ')
    potlatch2_preset.append(comment)

def fPresetsEnd():
    global potlatch2_preset, featureGroup
    # potlatch2_preset file needs to list twice the groups
    # 1. list of category, 2. list of include files
    # the  list of groups permits to treat these lists after reading all JOSM file
    #??? potlatch2_preset.append(featureGroup)
    tree=etree.ElementTree(potlatch2_preset)
    potlatch2_file="potlatch2_preset_test.xml"
    tree.write(potlatch2_file,xml_declaration=True,encoding='utf-8',method="xml",pretty_print=True )
    print "\nPOTLATCH2 OUTPUT : Main preset file\nFile=",potlatch2_file
    print "========================================================================="

def fGroup1Start():
    # JOSM first group level menu is ignored. In potlatch2, there is only one level
    return
    
def fGroup1End():
    # JOSM first group level menu is ignored. In potlatch2, there is only one level
    return
    
def ffeatureGroupStart():
# --------- first level group menu - add to groups_list ----------
    # JOSM second level menu group correspond to potlatch2 featureGroup
    # each featureGroup are saved in a separate file; include instructions are added to main file
    #   <group name="Highways" icon="presets/way_secondary.png">
    global JOSM_element, JOSM_node, JOSM_element, featureGroup_category, featureGroup, featureGroup_icon, groups_list, group_no
    if (JOSM_element.get("name")):
        featureGroup_category=JOSM_element.get("name")
    else:
        featureGroup_category="NoName"
        print "\nJOSM ERROR : no name specified in <group> Tag --> NoName will be used"
        fPrintCurrentElement()
    featureGroup=etree.Element("featureGroup")
    if (JOSM_element.get("icon")):
        featureGroup_icon=etree.Element("icon")
        featureGroup_icon_url=JOSM_element.get("icon")
        featureGroup_icon.set("image",featureGroup_icon_url)
        icon_font = etree.fromstring('<font size="14pt"><b>${name}</b></font>')
        # icon tag will be added to all feature sub-groups
    else:
        print "\nJOSM ERROR : ", featureGroup_category, " -> no icon specified in <group> Tag"
        fPrintCurrentElement()
    # adds group to groups_list (list used in cPresetsEnd() )
    groups_list.append(featureGroup_category)
    group_no=group_no+1

def ffeatureGroupEnd():
    global featureGroup, featureGroup_category, feature, featureGroup_icon, globals
    # if not </item> TAG before </group> TAG, we submit to save last item contents before group end
    if ('feature' in globals()):
        print "\nJOSM ERROR :  we save sub-items even if </item> TAG is missing before"
        fPrintCurrentElement()
        ffeatureEnd()
    category_fname="t"+featureGroup_category+".xml"
    tree=etree.ElementTree(featureGroup)
    tree.write(category_fname,xml_declaration=True,encoding='utf-8',method="xml",pretty_print=True )    
    print "\nPOTLATCH2 OUTPUT : Category preset file\nFile=", category_fname
    if ("featureGroup"  in globals()): del featureGroup
    if ("featureGroup_icon"  in globals()): del featureGroup_icon
  
def ffeatureGroupMissing():
    # If Group level 2 Tag is missing, adds featureGroup and prints Error message
    global JOSM_node, JOSM_element, featureGroup
    featureGroup=etree.Element("featureGroup")
    featureGroup_category="NoName"
    print "\n<group> TAG level 2 is missing before <sub-elements> : NoName used for category"
    fPrintCurrentElement()

def fSeparatorStart():
    # JOSM Separator add line between memu item. No correspondance in Potlatch2 and is ignored in the conversion.
    print "\nJOSM : <separator> TAG has no correspondance in Potlatch2. It will be ignored"
    fPrintCurrentElement()
    return
    
def fSeparatorEnd():
    # JOSM Separator add line between memu item. No correspondance in Potlatch2 and is ignored in the conversion.
    return

def ffeatureStart():
    # --------- second level group menu ----------
    """
     JOSM 
     second level menu group
          <item name="Road Restrictions" icon="presets/restrictions.png" type="node,way">
          <item name="Motorway Link" icon="presets/motorway.png" type="way">
     ->   <feature name="Motorway link">
           item type - potlatch2 docum specifies only line/point/area
          <item type="node" ->    <point/>
          <item type="way" ->    <line/>
          <item type="closedway" ->   <???area/>
          <item type="relation" ->    <???relation/> not documented but appears in potlatch2 defaultpresets
          <item type="node,way" ->    <point/><way/> 
     ->   <category>roads</category>
     ->   <icon image="features/highway__motorway_link.png"/>
    """
    global JOSM_element, featureGroup_category, feature, feature_category, feature_icon, icon_font
    #    if not ('featureGroup' in globals()):
    if not ('featureGroup' in globals()):
        ffeatureGroupMissing()
    # if previous item has no closed item, we submit to save previous item contents
    if ('feature' in globals()):
        print "\n</group> TAG missing before"
        fPrintCurrentElement()
        ffeatureEnd()
    feature=etree.Element("feature")
    feature_name=JOSM_element.get("name")
    feature.set("name",feature_name)
    feature_category=etree.Element("category")
    if featureGroup_category is not None :
        feature_category.text=featureGroup_category
        feature.append(feature_category)
    """
    # detect if icon attribute and then create icon tag
    if (JOSM_element.get("icon")):
        feature_icon=etree.Element("icon")
        feature_icon_url=JOSM_element.get("icon")
        feature_icon.set("image",feature_icon_url)
        icon_font = etree.fromstring('<font size="14pt"><b>${name}</b></font>')
        feature_icon.append(icon_font)
        feature.append(feature_icon)
    """
    # adds icon TAG from JOSM Group to each feature TAG
    if  ('featureGroup_icon' in globals()) :
        print etree.tostring(featureGroup_icon)
        feature.append(featureGroup_icon)
    # list of types
    ctypes=JOSM_element.get("type")
    # print etree.tostring(JOSM_element)
    if ctypes:
        ctypes=ctypes.replace('closedway','area')
        ctypes_list=ctypes.rsplit(',')
        for ctype in ctypes_list:
            if ctype=="node" : ctag=etree.Element("point")
            elif ctype=="way" : ctag=etree.Element("line")
            elif ctype=="closedway" : ctag=etree.Element("line")
            elif ctype=="relation" : ctag=etree.Element("relation")
            elif ctype=="relations" : ctag=etree.Element("relation")
            feature.append(ctag)ature=", etree.tostring(feature,pretty_print=True)
    
def ffeatureEnd():
    global feature, featureGroup
    if ('featureGroup' in globals()):
        featureGroup.append(feature)
        if 'feature'  in globals() : del feature

def ffeatureMissing():
    # If Item tag is missing, adds feature and prints Error message
    global JOSM_node, JOSM_element, feature
    feature=etree.Element("feature")
    feature_category="NoName"
    print "\nJOSM ERROR : <item> TAG is missing before"
    # print etree.tostring(JOSM_element, pretty_print=True)
    fPrintCurrentElement()

def fHelpStart():
    global JOSM_element, feature
    #    <link href="http://wiki.openstreetmap.org/wiki/Tag:highway=motorway"
    #       de.href="http://wiki.openstreetmap.org/wiki/DE:Tag:highway=motorway" />
    # -> <help>http://wiki.openstreetmap.org/wiki/Tag:highway%3Dmotorway</help>
    if not ('feature' in globals()):
        ffeatureMissing()
    help=etree.Element("help")
    help.text=JOSM_element.get("href")
    feature.append(help)

def fLineStart():
    global JOSM_element, feature
    #    <space />
    # -> <br/>
    if not ('feature' in globals()):
        ffeatureMissing()
    br=etree.Element("br")
    feature.append(br)

def fDescriptionStart():
    global JOSM_element, feature
    #    <label text="Edit Serviceway" />
    # -> <description  Access roads </description>
    if not ('feature' in globals()):
        ffeatureMissing()
    desc=etree.Element("description")
    desc.text=JOSM_element.get("text")
    feature.append(desc)

def fChoiceStart():
    #    <combo key="service" text="Serviceway type" values="alley,driveway,parking_aisle" default="" delete_if_empty="true" />
    # -> <input type="choice" presence="always" name="Type of service road" key="service" category="">
    # ->    <choice value="alley" text="Alleyway/laneway"/>
    # ->    <choice value="parking_aisle" text="Parking aisle" description="The path that cars drive on through a parking lot."/>
    # -> </input>
    global JOSM_element, feature
    if not ('feature' in globals()):
        ffeatureMissing()
    cinput=etree.Element("input")
    ckey=JOSM_element.get("key")
    ctext=JOSM_element.get("text")
    cvalues=JOSM_element.get("values")
    if (JOSM_element.get("default")):
        cdefault=JOSM_element.get("default")
        cinput.set("default",cdefault)
    cinput.set("type","choice")
    cinput.set("presence","always")
    cinput.set("name",ctext)
    cinput.set("key",ckey)
    # category attribute is derived from JOSM item name attribute
    if ('feature_name' in globals()) :
        cinput.set("category",feature_name)
    else:
        if (feature.get("name")) : ccategory=feature.get("name")
        else : ccategory=""
        cinput.set("category",ccategory)
    cinput.set("delete_if_empty","true")
    cvalues_list=cvalues.rsplit(',')
    for cvalue in cvalues_list:
        choice=etree.Element("choice")
        choice.set("value",cvalue)
        choice.set("text",cvalue)
        cinput.append(choice)
    feature.append(cinput)

def fTagStart():
    #    <key key="highway" value="motorway_link" />
    # -> <tag k="highway" v="motorway_link"/>
    # -> <tag k="man_made" v="survey_point" vmatch="survey_point|lighthouse|beacon|cairn|buoy"/>
    global JOSM_element, feature
    if not ('feature' in globals()):
        ffeatureMissing()
    ctag=etree.Element("tag")
    ckey=JOSM_element.get("key")
    cvalue=JOSM_element.get("value")
    ctag.set("k",ckey)
    ctag.set("v",cvalue)
    feature.append(ctag)

def fCheckboxStart():    
    #    <check key="oneway" text="Oneway" default="off" delete_if_empty="true" />
    # -> <input type="checkbox" presence="onTagMatch" category="Restrictions" key="area" name="Open area" description="The way is a large open space, like at a dock, where vehicles can move anywhere within the space, rather than just along the edge." />
    global JOSM_element, feature
    if not ('feature' in globals()):
        ffeatureMissing()
    ccheck=etree.Element("check")
    ckey=JOSM_element.get("key")
    ctext=JOSM_element.get("text")
    cdefault=JOSM_element.get("default")
    cdelete=JOSM_element.get("delete_if_empty")
    ccheck.set("type","checkbox")
    ccheck.set("presence","")
    ccheck.set("category","")
    ccheck.set("key",ckey)
    ccheck.set("name",ctext)
    ccheck.set("description","")
    feature.append(ccheck)

def fOptionalStart():    
    #    <optional>
    # -> ??? dont find this fonctionality in Potlatch2
    global JOSM_element, feature
    if not ('feature' in globals()):
        ffeatureMissing()
    coptional=etree.Element("optional")
    #feature.append(coptional)

def fEntity():
    # not documented in feature_maps.xml
    #     <within entity="way" k="highway" minimum="2"/>
    # - > ???
    return

def fRelation():
    # not documented in feature_maps.xml
    #     ???
    # ->  <tag k="route" v="hiking" vmatch="hiking|foot"/>
    return

def fTextStart():    
    #    <text key="name" text="Name" default="" delete_if_empty="true" />
    # -> ???<input type="freetext" category="Restrictions" presence="always" name="Start day"
    # key="day_on"   description="What day of the week does it start?" layout="horizontal" priority="low"/>
    global JOSM_element, feature, feature_category
    if not ('feature' in globals()):
        ffeatureMissing()
    cinput=etree.Element("input")
    if (JOSM_element.get("key")):
        ckey=JOSM_element.get("key")
    else:
        ckey="NoKey"
    if (JOSM_element.get("text")):
        ctext=JOSM_element.get("text")
    else:
        ctext="NoText"
    if (JOSM_element.get("default")):
        cdefault=JOSM_element.get("default")
    else:
        cdefault=""
    if (JOSM_element.get("delete_if_empty")):
        cdelete=JOSM_element.get("delete_if_empty")
    else:
        cdelete=""
    cinput.set("type","freetext")
    # category attribute is derived from JOSM item name attribute
    if ('feature_name' in globals()) :
        cinput.set("category",feature_name)
    else:
        if (feature.get("name")) : ccategory=feature.get("name")
        else : ccategory=""
        cinput.set("category",ccategory)
    cinput.set("key",ckey)
    cinput.set("presence","")
    feature_category=etree.Element("category")
    cinput.set("name",ctext)
    cinput.set("description","")
    feature.append(cinput)

def fCheckboxStart():    
    #    <check key="oneway" text="Oneway" default="off" delete_if_empty="true" />
    # -> <input type="checkbox" presence="onTagMatch" category="Restrictions" key="area" name="Open area" description="The way is a large open space, like at a dock, where vehicles can move anywhere within the space, rather than just along the edge." />
    global JOSM_element, feature
    if not ('feature' in globals()):
        ffeatureMissing()
    ccheck=etree.Element("check")
    ckey=JOSM_element.get("key")
    ctext=JOSM_element.get("text")
    cdefault=JOSM_element.get("default")
    cdelete=JOSM_element.get("delete_if_empty")
    ccheck.set("type","checkbox")
    ccheck.set("presence","")
    ccheck.set("category","")
    ccheck.set("key",ckey)
    ccheck.set("name",ctext)
    ccheck.set("description","")
    feature.append(ccheck)

def fMultiSelectStart():
    #    <multiselect key="cuisine" text="Cuisine" values="italian;chinese;pizza;burger;greek;german;indian;regional;kebab;turkish;asian;thai;mexican;japanese;french;sandwich;sushi" default=""/>
    #     values: delimiter-separated list of values (delimiter can be escaped with backslash)
    #     display_values: delimiter-separated list of values to be displayed instead of the
    #     database values, order and number must be equal to values
    #     short_description: delimiter-separated list of texts to be displayed below each
    # ->  Not found in potlatch2 : we treat like combo
    fChoiceStart()
    
def fRolesStart():
    #    <roles>
    if not ('feature' in globals()):
        ffeatureMissing()
    return
    
def fRolesEnd():
    #    </roles>
    return

def fRoleStart():
    #    <role key="outer" text="outer segment" requisite="required" type="way" />
    if not ('feature' in globals()):
        ffeatureMissing()
    return

"""
===============================================================================
 Main routine : parse JOSM presets and convert to potlatch2
===============================================================================
"""

JOSM_presets = etree.iterparse(infile, events=("start", "end"))

#print etree.tostring(JOSM_presets, encoding="utf-8",method="xml",pretty_print=True)
#print "========================================================================="
#for JOSM_event, JOSM_element in JOSM_presets:
#    print etree.find(".")
    #subElement(JOSM_element),pretty_print=True)

#print "========================================================================="

#logfile = open('test.log', 'w')
#logfile.write('test succeeded')
#logfile.close()

#===============================================================================
#<presets>
#<!-- *** group Humanitarian *** -->
#<group name="Humanitarian Features - Common Tags">
#<!-- *** item ID *** -->
#<item name="ID">
#<text key="id:uuid" text="ID:UUID"/>

group_no=0
groups_list=[]
JOSM_node=0
for JOSM_event, JOSM_element in JOSM_presets:
    JOSM_node=JOSM_node+1

#  if JOSM_event=="start":
    parent=JOSM_element.getparent()
    '''
    if JOSM_node>0:
        prec=JOSM_element.getprevious()
        txt_element=etree.tostring(prec)
        colend=txt_element.find("-->")+3
        if colend>1:
            print "\nCOMMENT before JOSM_element"
            print txt_element[0:colend], "\n***************************************"
    '''
    
    """
    # node 1 : modify Tag name when Namespace is specified on presets tag
    #ie. {http://josm.openstreetmap.de/tagging-preset-1.0}presets"
    if JOSM_node ==1:
        txt=JOSM_element.tag
        print "JOSM_element.tag", JOSM_element.tag
        iPresets=txt.find("presets")
        print "iPresets=", iPresets
        if iPresets>=1 : JOSM_element.tag="presets"
        print "JOSM_element.tag", JOSM_element.tag
        if (JOSM_element.find("presets")>=1): print "OUI PRESETS"
        print "DEBUG JOSM_node=", JOSM_node, ", JOSM_event=", JOSM_event, JOSM_element.tag
        fPrintCurrentElement()
    """    
    # --------- presets ==> mapFeatures ----------
    ### if (JOSM_node==1 and iPresets>=1 and (JOSM_event=="start")):
    if ((JOSM_element.tag=="presets") and (JOSM_event=="start")):
        fPresetsStart ()
        iPresets=0
    # --------- presets ==> write potlatch2 preset main file ----------
    elif (JOSM_element.tag=="presets") and (JOSM_event=="end"):
        fPresetsEnd ()
    # --------- groups ----------
    # group menu - two levels exist
    # elif (JOSM_element.tag=="group") and (JOSM_event=="start"):
    # --------- first level group menu - ignore this first level of menu ----------
    elif (JOSM_element.tag=="group") and (parent.tag<>"group") and JOSM_event=="start":
        fGroup1Start()
    elif (JOSM_element.tag=="group") and (parent.tag<>"group") and JOSM_event=="end":
        fGroup1End()
    # --------- second level group menu ----------
    elif (JOSM_element.tag=="group") and (parent.tag=="group") and (JOSM_event=="start"):
        ffeatureGroupStart()
    # end of featureGroup - add category and include instructions + write potlatch2 feature file
    elif  (JOSM_element.tag=="group") and (parent.tag=="group") and (JOSM_event=="end"):
        ffeatureGroupEnd()
    # --------- separator line in JOSM preset menu ----------
    elif (JOSM_element.tag=="separator") and JOSM_event=="start":
        fSeparatorStart()
    elif (JOSM_element.tag=="separator") and JOSM_event=="end":
        fSeparatorEnd()
    # --------- items ----------
    elif (JOSM_element.tag=="item") and (JOSM_event=="start"):
        ffeatureStart()
    # end of item - append to feature
    elif (JOSM_element.tag=="item") and (JOSM_event=="end"):
        ffeatureEnd()
        # --------- link -> help ----------
    elif (JOSM_element.tag=="link") and (JOSM_event=="start"):
        fHelpStart()
    elif (JOSM_element.tag=="link") and (JOSM_event=="end"):
        pass
    # --------- space -> br ----------
    elif (JOSM_element.tag=="space") and (JOSM_event=="start"):
        fLineStart()
    elif (JOSM_element.tag=="space") and (JOSM_event=="end"):
        pass
    # --------- label -> description ----------
    elif (JOSM_element.tag=="label") and (JOSM_event=="start"):
        fDescriptionStart()
    elif (JOSM_element.tag=="label") and (JOSM_event=="end"):
        pass
    # --------- combo -> choice ----------
    elif (JOSM_element.tag=="combo") and (JOSM_event=="start"):
        fChoiceStart()
    elif (JOSM_element.tag=="combo") and (JOSM_event=="end"):
        pass
    # --------- key -> tag ----------
    elif (JOSM_element.tag=="key") and (JOSM_event=="start"):
        fTagStart()
    elif (JOSM_element.tag=="key") and (JOSM_event=="end"):
        pass
    # --------- check -> input type="checkbox" ----------
    elif (JOSM_element.tag=="check") and (JOSM_event=="start"):
        fCheckboxStart()
    elif (JOSM_element.tag=="check") and (JOSM_event=="end"):
        pass
    # --------- optional ->  ----------
    elif (JOSM_element.tag=="optional") and (JOSM_event=="start"):
        fOptionalStart()
    elif (JOSM_element.tag=="optional") and (JOSM_event=="end"):
        pass
    # --------- text ->  ----------
    elif (JOSM_element.tag=="text") and (JOSM_event=="start"):
        fTextStart()
    elif (JOSM_element.tag=="text") and (JOSM_event=="end"):
        pass
    # to verify if all TAGS have been treated
    else:
        print JOSM_event, "EVENT TAG not treated"
        fPrintCurrentElement()

"""
===============================================================================
 PARSING XML completed
 Builds Potlatch2 presets main file
 adds category and include instructions
===============================================================================
"""

# potalch2_preset file : adds category
comment = etree.Comment(' Categories ')
potlatch2_preset.append(comment)
group_no=0
for group in groups_list:
    #    <group name="Humanitarian Features - Common Tags">
    #==> <category name="Humanitarian" id="Humanitarian"/>
    category=etree.Element("category")
    category.set("name",group)
    potlatch2_preset.append(category)

# potalch2_preset file : adds include tags
comment = etree.Comment(' Features ')
potlatch2_preset.append(comment)
group_no=0
for group in groups_list:
    #    <group name="Humanitarian Features - Common Tags">
    #==> <include file="Humanitarian" id="Humanitarian.xml"/>
    category=etree.Element("include")
    category.set("name",group+".xml")
    potlatch2_preset.append(category)

#=========================================================================
infile.close()
