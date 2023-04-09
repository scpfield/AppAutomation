import sys, io, time, random, json
import xml.etree.ElementTree as ET, lxml.html, lxml.etree
from copy import copy

#from itertools import *
#from more_itertools import *

import selenium.webdriver
import appium.webdriver

import app_config
import apps
import app_elements
from app_elements import JSONSerializer
from util import *

class AppPageInitFailException(Exception):
    ...

class AppPage():
    
    def __init__( self, *args, **kwargs ):
        for Key, Value in kwargs.items(): 
            setattr(self, Key, Value)
        ...
    
    
    @classmethod
    def GetPageSource(cls):
        print('AppPage: Loading page source from Driver')
        return app_config.Driver.page_source    
        ...

    def PageSourceToFile(self, FileName = 'page_source.xml', Randomize = False):
        if Randomize: 
            FileName = FileName.replace('.xml', '_' + self.PageName + '_' + RandomString(5) + '.xml')
        else:
            FileName = FileName.replace('.xml', '_' + self.PageName + '.xml')
            
        print('PageSourceToFile: Writing to file: ' + FileName)

        with open( FileName, 'w+', newline = '', encoding = 'utf-8') as OutputFile:
            OutputFile.write( str(self.GetPageSource()) )
        ...

    def ElementTreeToFile(self, FileName = 'element_tree.json', Randomize = False):
        return
        if Randomize: 
            FileName = FileName.replace('.json', '_' + self.PageName + '_' + RandomString(5) + '.json')
        else:
            FileName = FileName.replace('.json', '_' + self.PageName + '.json')
            
        print('ElementTreeToFile: Writing to file: ' + FileName)
                    
        with open( FileName, 'w+', newline = '', encoding = 'utf-8' ) as OutputFile:
            OutputFile.write( json.dumps( 
                app_config.CurrentPage.PageElementTree, default = JSONSerializer, indent = 1 ))
        ...

    def EnumerateElementTree(self):
    
        MaxNameLen = 0
        for Node in self.PageElementTree.Descendants():
            #print("Node = ", Node)
            #print(str(self.PageElementTree.Lists))
            if len(Node.Name) > MaxNameLen:
                MaxNameLen = len(Node.Name)

        for Node in self.PageElementTree.Descendants():
            #print("node = ", Node)
            #print(str(self.PageElementTree.Lists))
            Spaces = (' ' * ( (MaxNameLen - len(Node.Name)) + 2))
            print(f"{Node.Name}{Spaces}: {Node.ObjPath}", Decorate=False)
            
            
    @classmethod
    def CreateElementTree( cls,
                           XMLNode       = None, 
                           CurrentNode   = None, 
                           ObjPath       = '',
                           XPath         = '',
                           Level         = 0,
                           NodeTagCounts = None ):
        
        if XMLNode == None:
            XMLTree =   ET.canonicalize(
                            xml_data    = cls.GetPageSource(), 
                            strip_text  = True) 
            XMLNode =   ET.fromstring( XMLTree )
        ...
        
        # make up a name for a new python object node
        ShortTagName = XMLNode.tag.split('.')[-1].split('}')[-1]
        XPath += ('/' + ShortTagName) 
        ElementName = ''
        
        if NodeTagCounts == None:
            NodeTagCounts = {}
        
        # to generate unique object names, if the XML element
        # has an index attribute, use that.  otherwise, keep
        # track of the count of duplicate tag names in the 
        # same level with a dictionary using the python id()
        # as the key
        
        if 'index' not in XMLNode.attrib:
        
            NodeKey = 0
            
            if CurrentNode != None:
                NodeKey = hash(CurrentNode)
            
            if NodeKey in NodeTagCounts:
                if ShortTagName in NodeTagCounts[NodeKey]:
                    NodeTagCounts[NodeKey][ShortTagName] += 1
                else:
                    NodeTagCounts[NodeKey][ShortTagName] = 0
            else:
                NodeTagCounts[NodeKey] = {}
                NodeTagCounts[NodeKey][ShortTagName] = 0
                
            ElementName = str(
                ShortTagName + '_' + 
                str(NodeTagCounts[NodeKey][ShortTagName]) )    
        
        else:
            ElementName = str(
                ShortTagName + '_' + 
                str( XMLNode.attrib['index'] ))        
        
        
        if not CurrentNode:
            ObjPath += ElementName
        else:
            ObjPath += ( '.' + ElementName )
        
        # convert xml attribute values to python data types
        ElementAttrs = {}
        for XMLAttrName in XMLNode.attrib:
        
            XMLAttrValue = XMLNode.attrib[XMLAttrName]
            
            if ( ( XMLAttrValue == None ) or 
                 ( XMLAttrValue == '' ) ):
                 ElementAttrs[XMLAttrName] = None
                 continue
            
            if IsInt( XMLAttrValue ):
                ElementAttrs[XMLAttrName] = int(XMLAttrValue)
                continue
            
            if IsFloat( XMLAttrValue ):
                ElementAttrs[XMLAttrName] = float(XMLAttrValue)
                continue
            
            if ((XMLAttrValue == 'true') or
                (XMLAttrValue == 'True')): 
                    ElementAttrs[XMLAttrName] = True
                    continue
        
            if ((XMLAttrValue == 'false') or
                (XMLAttrValue == 'False')):
                    ElementAttrs[XMLAttrName] = False
                    continue

            
            if  (( XMLAttrName == 'bounds' )            and
                 ( XMLAttrValue[0]  == '[' )            and
                 ( XMLAttrValue[-1] == ']' )            and
                 ( '][' in XMLAttrValue    )):
                    XMLAttrValue  = XMLAttrValue.replace('[', ' ')
                    XMLAttrValue  = XMLAttrValue.replace(']', ' ')
                    XMLAttrValue  = XMLAttrValue.replace(',', ' ')
                    XMLAttrValue  = list(map(int, XMLAttrValue.split()))
                    X1 = XMLAttrValue[0]
                    Y1 = XMLAttrValue[1]
                    X2 = XMLAttrValue[2]
                    Y2 = XMLAttrValue[3]
                    ElementAttrs[XMLAttrName] = { 'X1' : X1, 
                                                  'Y1' : Y1, 
                                                  'X2' : X2, 
                                                  'Y2' : Y2 }
                                                  
                    ElementAttrs[XMLAttrName]['Width'  ] = ( X2 - X1 )
                    ElementAttrs[XMLAttrName]['Height' ] = ( Y2 - Y1 )
                    ElementAttrs[XMLAttrName]['CenterX'] = int(( 
                        ElementAttrs[XMLAttrName]['Width'  ] / 2 ) + X1 )
                    ElementAttrs[XMLAttrName]['CenterY'] = int(( 
                        ElementAttrs[XMLAttrName]['Height' ] / 2 ) + Y1 )
               
                    continue
            
            ElementAttrs[XMLAttrName] = str(XMLAttrValue)
            
        ...  # end of attribute type converting    
        
        NewNode = cls.NewElement( Name        = str( ElementName ),
                                  Tag         = ShortTagName,
                                  Text        = XMLNode.text,
                                  Tail        = XMLNode.tail,
                                  Attributes  = dict( ElementAttrs ),
                                  ObjPath     = str( ObjPath ),
                                  XPath       = str( XPath ),                                     
                                  Selector    = cls.GetSelector( XMLNode ),
                                  Locator     = cls.GetLocator( XMLNode ),
                                  Instance    = None )
        
        if NewNode == None:
            print('Failed to create new node for: ' + Name + ' ' + ObjPath)
        
        # add parent
        setattr(NewNode, 'Parent', CurrentNode)

        # add new object as child object
        if CurrentNode == None:
            CurrentNode = NewNode
        else:
            setattr(CurrentNode, NewNode.Name, NewNode)

        
        # process child XML nodes    
        for XMLChildNode in XMLNode:
            
            Node = cls.CreateElementTree(   XMLNode     = XMLChildNode, 
                                            CurrentNode = NewNode, 
                                            ObjPath     = ObjPath,
                                            XPath       = XPath,
                                            Level       = (Level + 1),
                                            NodeTagCounts = NodeTagCounts)
                                            
        return CurrentNode
    ...


class MobileAppPage( AppPage ):

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        ...


class AndroidAppPage( MobileAppPage ):

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )

        self.PageElementTree = AndroidAppPage.CreateElementTree()
        print('Created new ElementTree')
        
        if not self.PageElementTree:
            raise AppPageInitFailException
        ...
        
    @classmethod
    def NewElement( cls, *args, **kwargs ):
    
        return app_elements.AndroidElement.NewElement( *args, **kwargs )
        
    @classmethod
    def GetLocator( cls, SourceNode ):
        return app_elements.AndroidElement.LOCATOR_ANDROID                

    @classmethod
    def GetSelector( cls, SourceNode ):
        
        SourceAttrs = SourceNode.attrib
        
        # create generic Android UiSelector
        Selector = str( 'new UiSelector()' )

        ResourceId = SourceAttrs.get('resource-id')
        if ResourceId: Selector += f".resourceId(\"{ResourceId}\")"

        ClassName = SourceAttrs.get('class')
        if ClassName: Selector += f".className(\"{ClassName}\")"
        
        ContentDesc = SourceAttrs.get('content-desc')
        if ContentDesc: Selector += f".description(\"{ContentDesc}\")"
        
        Text = SourceAttrs.get('text')
        if Text: Selector += f".text(\"{Text}\")"
            
        Index = SourceAttrs.get('index')
        if Index: Selector += f".index({Index})"
            
        # make it a UiScrollable selector if scrollable
        Scrollable = SourceAttrs.get('scrollable')
        
        if (( Scrollable == 'true' ) or
            ( Scrollable == True   )): 
            Selector += f".scrollable(true)"
            Selector = f"new UiScrollable({Selector})"
        
        return Selector
        ...

        
class WebAppPage( AppPage ):

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )

        self.PageElementTree = WebAppPage.CreateElementTree()
        print('Created new ElementTree')
        
        if not self.PageElementTree:
            raise AppPageInitFailException
        ...        
        
    @classmethod
    def NewElement( cls, *args, **kwargs ):
        return app_elements.WebAppElement.NewElement( *args, **kwargs )
        
    @classmethod
    def GetPageSource( cls ):
        print('WebAppPage: GetPageSource called')
        return  lxml.etree.tostring(
                lxml.html.fromstring( 
                super().GetPageSource()))
        ...
    
    @classmethod
    def GetLocator( cls, SourceNode ):
        return app_elements.WebAppElement.LOCATOR_CSS
     
    @classmethod
    def GetSelector( cls, SourceNode ):
        
        ExcludeChars = [ '[', ']', '{', '}', '<', '>', '\n', '\r', 
                        '\t', '`', '\\', '|', '=', '*', '"', '\'' ]

        ShortTagName = SourceNode.tag.split('.')[-1].split('}')[-1]
        Selector = str( ShortTagName )
        
        for Name in SourceNode.attrib:
            Skip = False
            if ((SourceNode.attrib[Name] == None) or
                (SourceNode.attrib[Name] == '')):
                Skip = True
            else:
                for ExcludeChar in ExcludeChars:
                    if ExcludeChar in SourceNode.attrib[Name]:
                        Skip = True
                        break
            if not Skip:
                Selector += f'[{Name}="{SourceNode.attrib[Name]}"]'

        return Selector  
        ...    


if __name__ == '__main__':
    print('app_pages: Hello, world')
    
    