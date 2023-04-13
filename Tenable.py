import sys, time, random

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
    
    
    
    def Test( self ):
         
        if not self.Logon():
            print('Failed to logon')
            self.ExitApp()
            return False

        if not self.CreateAllScans():
            print('Failed to create scans')
            self.ExitApp()
            return False
            
            
        Pause("Test Complete")
        
        self.ExitApp()
        quit()
    
    


if __name__ == '__main__':

    MyTestApp = TenableApp( UseAppium=False)
    MyTestApp.Test()



