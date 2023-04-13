import sys, io, time, random, json, xml.etree.ElementTree as ET, lxml.html, lxml.etree
from copy import copy
from more_itertools import ncycles

import selenium.webdriver
from selenium.webdriver.remote.command import *
import appium.webdriver

from apps import *
import app_config
import app_pages
import app_elements
from util import *


class TenableApp( WebApp ):

    def __init__( self, UseAppium = False ):
        super().__init__( UseAppium )        
    ...

    def DumpResult( self, Result, Node=None ):
        
        print()
        print('---------------------------------')
        if Node!= None:
            print(Node.ObjPath)
            print(Node.XPath)
        print('.................................')
        
        Pause()
        
        if Result:
        
            if isinstance(Result, list):
            
                for Idx, Item in enumerate(Result):
                    
                    print("LIST ITEM #", Idx)
                    print("------------")
                    if isinstance(Item, dict):
                        
                        print("DICT ITEM")
                        print("------------")
                        
                        for Key, Value in Item.items():
                            
                            print(Key, '     ', str(Value))
                            
                            if Key != 'dispatchEvent':
                                continue
                            
                            if isinstance(Value, list):
                            
                                for ValueItem in Value:
                                    
                                    if isinstance(ValueItem, dict):
                                    
                                        for Key2, Value2 in ValueItem.items():
                                        
                                            print(Key2, Value2)
                                            
                            print(str(Value))
                            
                            
                    else:
                        print(type(Item))
                        print(str(Item))
                        Pause("Next List Item")
                
                return
                
            if isinstance(Result, str):
                print(Result, Decorate=False)
                return
            
            
            print()
            print(type(Result))
            print(str(Result))
            return
            
        else:
            print("No Result")
    
    def Logon( self ):

        LogonURL    = 'https://localhost:8834/'
        WaitFor     = { 'Tag' : 'button', 'type' : 'submit' }
                
        if not self.LoadPage( PageName = "LogonPage",
                              Target = LogonURL, 
                              WaitFor = WaitFor ):
            print('Failed to load page: ' + LogonURL)
            return False

        LogonPageRoot   = self.LogonPage.PageElementTree

        UsernameField = ([  Element
                            for  Element  in  LogonPageRoot.Descendants()
                            if   isinstance( Element, app_elements.EditableElement )
                            if   getattr(    Element, 'aria-label' ) == 'Username' ])[0]
        
        
        PasswordField = ([  Element
                            for  Element  in  LogonPageRoot.Descendants()
                            if   isinstance( Element, app_elements.EditableElement )
                            if   getattr(    Element, 'aria-label' ) == 'Password' ])[0]
        

        LogonButton   = ([  Element
                            for  Element  in  LogonPageRoot.Descendants()
                            if   isinstance( Element, app_elements.ClickableElement )
                            if   getattr(    Element, 'type' ) == 'submit' 
                            if   getattr(    Element.Parent, 'class' ) == 'login' ])[0]
        
    
        UsernameField.SendKeys("scpfield")
        PasswordField.SendKeys("admin")
        LogonButton.Click()
        
        WaitFor = { 'Tag' : 'div', 'data-domselect' : 'main-scroll-to-top' }
        
        if not self.LoadPage( PageName = "HomePage", WaitFor = WaitFor ):
            print('Failed to load HomePage');
            return False
        else:
            return True
    
    
    def AddCredential(self, CredentialsButton ):
    
            CredentialsButton.Click()
            
            WaitFor = { 'Tag' : 'li', 'data-name' : 'Windows' }
            
            if not self.LoadPage( PageName = "CredentialsPage", WaitFor = WaitFor ):
                print('Failed to load CredentialsPage');
                return False
                    
            CredentialsPageRoot = self.CredentialsPage.PageElementTree
            
            WindowsButton   = ([  Element
                                  for Element in CredentialsPageRoot.Descendants()
                                  if isinstance( Element, app_elements.ClickableElement )
                                  if getattr( Element, 'data-name' ) == 'Windows' ])[0]
                                  
            WindowsButton.Click()
            
            WaitFor = { 'Tag' : 'div', 'data-input-id' : 'start_server_service' }
            
            if not self.LoadPage( PageName = "WindowsPage", WaitFor = WaitFor ):
                print('Failed to load WindowsPage');
                return False
                
            WindowsPageRoot = self.WindowsPage.PageElementTree
                
            UsernameField = ([  Element
                                for  Element  in  WindowsPageRoot.Descendants()
                                if   isinstance( Element, app_elements.EditableElement )
                                if   getattr( Element, 'aria-label' ) == 'Username' 
                                for  Ancestor in  Element.Ancestors()
                                if   getattr( Ancestor, 'data-parent-id' ) == 'auth_method'
                                if   'hide' not in getattr( Ancestor, 'class' ) ])[0]

            PasswordField = ([  Element                            
                                for  Element  in  WindowsPageRoot.Descendants()
                                if   isinstance( Element, app_elements.EditableElement )
                                if   getattr( Element, 'aria-label' ) == 'Password' 
                                for  Ancestor in  Element.Ancestors()
                                if   getattr( Ancestor, 'data-parent-id' ) == 'auth_method'
                                if   'hide' not in getattr( Ancestor, 'class' ) ])[0]
                            
            UsernameField.SendKeys('Administrator')
            PasswordField.SendKeys('admin')

            return True
    
    
    
    def CreateScan(self, CategoryElement, CategoryTitle ):
    
        CategoryElement.Click()
        
        WaitFor = { 'Tag' : 'input', 'data-name' : 'Name' }
        
        if not self.LoadPage( PageName = "NewScanPage", WaitFor = WaitFor ):
            print('Failed to load NewScanPage');
            return False
        
        NewScanPageRoot = self.NewScanPage.PageElementTree
        
        NameField    = ([  Element
                           for Element in NewScanPageRoot.Descendants()
                           if isinstance( Element, app_elements.EditableElement )
                           if getattr( Element, 'aria-label' ) == 'Name' ])[0]
        
        TargetsField = ([ Element
                          for Element in NewScanPageRoot.Descendants()
                          if isinstance( Element, app_elements.EditableElement )
                          if getattr( Element, 'aria-label' ) == 'Targets' ])[0]
        
        SaveButton   = ([  Element
                           for Element in NewScanPageRoot.Descendants()
                           if isinstance( Element, app_elements.ClickableElement )
                           if getattr( Element, 'data-action' ) == 'save' ])[0]
                          
        
        if not NameField or not TargetsField or not SaveButton:
            print('Failed to locate elements')
            return False

        NameField.SendKeys( 'My ' + CategoryTitle )
        TargetsField.SendKeys( '172.16.0.35, 172.16.34.156' )
        
        
        if CategoryTitle == 'Advanced Dynamic Scan':
        
            DynamicPluginsButton  = (
                [   Element
                    for Element in NewScanPageRoot.Descendants()
                    if isinstance( Element, app_elements.ClickableElement )
                    if getattr( Element, 'data-name' ) == 'dynamic-plugins' ])[0]
                    
            DynamicPluginsButton.Click()
            
            WaitFor = { 'Tag' : 'input', 'data-name' : 'Result Filter Control Input' }
            
            if not self.LoadPage( PageName = "DynamicPluginsPage", WaitFor = WaitFor ):
                print('Failed to load DynamicPluginsPage');
                return False

            DynamicPluginsPageRoot = self.DynamicPluginsPage.PageElementTree
            
            CVEField    = ([ Element
                             for Element in DynamicPluginsPageRoot.Descendants()
                             if isinstance( Element, app_elements.EditableElement )
                             if getattr( Element, 'data-name' ) == 'Result Filter Control Input' ])[0]
                             
            CVEField.SendKeys( 'CVE-2011-0018' )
        
        
        if (( CategoryTitle == 'Malware Scan' ) or
            ( CategoryTitle == 'Credentialed Patch Audit' )):
        
            CredentialsButton  = ([  Element
                                     for Element in NewScanPageRoot.Descendants()
                                     if isinstance( Element, app_elements.ClickableElement )
                                     if getattr( Element, 'data-name' ) == 'credentials' ])[0]
             

            self.AddCredential( CredentialsButton )
            

            
        SaveButton.Click()

        return True
        
        
    
    def CreateAllScans(self):

        HomePageRoot    = self.HomePage.PageElementTree
        NewScanButton   = ([  Element
                              for  Element  in  HomePageRoot.Descendants()
                              if   isinstance( Element, app_elements.ClickableElement )
                              if   getattr(    Element, 'id' ) == 'new-scan' ])[0]
                              
        if NewScanButton:
            NewScanButton.Click()
        else:
            return False

        WaitFor = { 'Tag' : 'div', 'class' : 'library' }
        
        if not self.LoadPage( PageName = "ScanTemplatesPage", WaitFor = WaitFor ):
            print('Failed to load ScanTemplatesPage');
            return False
        
        ScanTemplatesPageRoot  = self.ScanTemplatesPage.PageElementTree

        Categories  = ([    Element
                            for  Element in ScanTemplatesPageRoot.Descendants()
                            if   hasattr( Element, 'data-category' )
                            if   getattr( Element, 'class' ) == 'category-templates' ])
        
        for Category in Categories:
        
            CategoryName = getattr( Category, 'data-category' )
            
            print( f"Category: {CategoryName}" )
            
            CategoryItems = ([  ( Element, Child.Text )
                                for  Element in Category.Descendants()
                                for  Child in Element.Descendants()
                                if   isinstance( Element, app_elements.ClickableElement )
                                if   getattr( Element, 'data-category' ) == CategoryName
                                if   ( { 'class' : 'banner' }, True ) not in Element
                                if   getattr( Child, 'class' ) == 'title'
                            ])
            
            
            for CategoryElement, CategoryTitle in CategoryItems:
            
                print("Creating Scan for: " + CategoryTitle)
                
                if not ( self.CreateScan( CategoryElement, CategoryTitle )):
                    return False
                
                time.sleep(3)
                NewScanButton.Instance = None
                NewScanButton.Click()
                
                
                
            
        
        return True
        
        
        
    
    def Test( self ):
         
        if not self.Logon():
            print('Failed to logon')
            self.ExitApp()
            return False

        if not self.CreateAllScans():
            print('Failed to create scans')
            self.ExitApp()
            return False
            
        
        #if Result:
        #    print(str(Result))
        #    self.DumpResult( Result, UsernameField )
        #else:
        #    print("No Result")
            
        
        
        #UsernameField.SetAttribute("value", "Administrator")
        #PasswordField.Click()
        #PasswordField.SetAttribute("value", "admin")
            
        Pause("Test Complete")
        
        self.ExitApp()
        quit()
    
        '''
        LogonButton  = ([   Element
                            for Element in RootNode.Descendants()
                            if  Element.Name == 'button_0'
                            if  getattr( Element.Parent, 'id' ) == 'start' 
                            ])[0]
                                
        '''    
        #Result = app_config.Driver.execute( Command.W3C_EXECUTE_SCRIPT,
        #                                    {  'script' : Script,
        #                                       'args'  : Args     })
            
    




if __name__ == '__main__':

    MyTestApp = TenableApp( UseAppium=False)
    MyTestApp.Test()




'''
            Script = "$('#start').hide();"
            Script = "return document.getElementById('start')"
            Script = "return document.getElementById('start').nodeName"
            Script = "return document.getElementById('start').nodeType"
            Script = "return document.documentElement.firstChild"
            Script = "return document.activeElement.nodeName"
            Script = "return document.fonts"
            Script = "return document.implementation"
            Script = "return document.scripts"
            Script = "return document.scripts[0].nodeName"
            Script = "return document.scripts[0].firstChild"
            Script = "return document.getElementById('start').getAttribute('id')"
            Script = "return document.getElementById('start').childNodes[0].nodeValue"
            Script = "return document.getElementById('start').innerHTML"
            Script = "return document.getElementById('start').attributes"
            Script = "return document.getElementById('start').id"
            Script = "return document.getElementById('start').childNodes[0].nextSibling.nodeName"
            Script = "return document.getElementById('start').childNodes[0].nextSibling.childNodes[0].replaceData('Foobar')"
            Script = "return (document.getElementById('start').childNodes[0].nextSibling.childNodes[0].data = 'foobar')"
            Script = "return (document.getElementById('start').childNodes[1].childNodes[0].data = 'foobar')"
            Script = "return document.documentElement.querySelector('button').innerHTML;"
            Script = "return document.getElementById('start').childNodes[0].nextSibling.innerHTML;"
            Script = "return document.getElementById('start').childNodes[1].innerHTML;"
            Script = "document.getElementById('start').childNodes[1].innerHTML = 'foobar';"            
            Script = "return ( document.querySelector('button').innerHTML = 'HackerRank Test For Tenable' );"
            Script = "return ( document.querySelector('button').setAttribute('style','display:none'))"
            Script = "return document.querySelector('document.children[0].children[1].children[1].children[2].children[1]');"
'''


'''
                #Script = ( Node.DOMPath + ".dispatchEvent(new MouseEvent('click', " +
                #            "{ bubbles    : true, " +
                #            "  cancelable : true, " +
                #            "  view       : window, } ));" )

                Script1 = ( "return (" + Node.DOMPath + ".dispatchEvent(new FocusEvent('focus', " +
                            "{ bubbles    : true, " +
                            "  cancelable : true, " +
                            "  button     : 0, " +
                            "  view       : window } )));" )

                Script2 = ( "return (" + Node.DOMPath + ".dispatchEvent(new MouseEvent('click', " +
                            "{ bubbles    : true, " +
                            "  cancelable : true, " +
                            "  button     : 0, " +
                            "  view       : window  } )));" )
                            
                            
                Script3 = ( "return (" + Node.DOMPath + ".dispatchEvent(new MouseEvent('mousedown', " +
                            "{ bubbles    : true, " +
                            "  cancelable : true, " +
                            "  button     : 0, " +
                            "  view       : window } )));" )
                            

                Script4 = ( Node.DOMPath + ".dispatchEvent(new MouseEvent('mouseup', " +
                            "{ bubbles    : true, " +
                            "  cancelable : true, " +
                            "  button     : 0, " +
                            "  view       : window } ));" )



        # <section id="notifications">
        #   <div role="alert" class="notification error" data-id="d7697b5b-784c-42eb-b638-f6eab0446efa" data-notification-id="">
        #    <div class="notification-message">Error: Invalid Credentials</div>

'''
   
   