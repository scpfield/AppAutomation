import sys, io, time, random, json, xml.etree.ElementTree as ET, lxml.html, lxml.etree
from copy import copy

import selenium.webdriver
import appium.webdriver

import app_config
import app_pages
import app_elements
from util import *



class DriverInitException(Exception):
    ...
    
class TestApp():
    
    START_PAGE_KEY = 'StartPage'
    
    def __init__( self, UseAppium = True ):
        if not self.InitializeDriver( UseAppium ):
            raise DriverInitException
        
        self.Page = app_config.Container()
        app_config.Page = self.Page
        app_config.App  = self
        ...
    
    def StartApp( self ):
        ...
    
    def ExitApp( self ):
        if app_config.Driver:
            print('Closing app_config.Driver')
            app_config.Driver.quit()
            app_config.Driver = None
            return True
        else: 
            print('No app_config.Driver to close')
            return False
        ...

    def WaitForPage( self, WaitForResourceId ):
        ...            
        
    def InitializeDriver( self, UseAppium ):
        ...
    
    def GetStartPage( self ):
        ...
        
... # end of TestApp base class
    
    
class WebApp( TestApp ):

    def __init__( self, UseAppium = True ):
        print('Called')
        super().__init__( UseAppium )
        self.CurrentActivity = ''
        ...

    @classmethod
    def NewPage( cls, *args, **kwargs ):
                            
        print('Creating new WebAppPage')
        
        # intercept args and adjust if needed
        App         = kwargs['App']
        PageName    = kwargs['PageName']
        UniqueName  = None
        
        # check if the requested page already exists
        if hasattr(App, PageName):
        
            print("Page name collision")
            
            # append random string to requested page name
            UniqueName = PageName + '_' + RandomString(5)
            
            kwargs['PageName'] = UniqueName
            print('Renamed page to: ' + UniqueName)
            
        NewPage = None
        NewPage = app_pages.WebAppPage( *args, **kwargs )   
        setattr( App, NewPage.PageName, NewPage )
        App.CurrentPage             = NewPage
        app_config.CurrentPage      = NewPage
        return NewPage
        ...
    
    def InitializeDriver(self, UseAppium = True ):
        
        try:
            if not UseAppium:
                print('Initializing Selenium app_config.Driver')
                
                CapabilityParameters = {}
                Capabilities = {}
                CapabilityParameters['acceptInsecureCerts'] = True
                CapabilityParameters['unhandledPromptBehavior'] = 'dismiss'
                CapabilityParameters['pageLoadStrategy'] = 'normal'
                Capabilities['capabilities'] = {}
                Capabilities['capabilities']['alwaysMatch'] = CapabilityParameters                    
                
                app_config.Driver = selenium.webdriver.Chrome(desired_capabilities=Capabilities)
                
            else:
                print('Initializing Appium app_config.Driver' )
                AppiumServer = 'http://127.0.0.1:4723'
                Capabilities = {}
                Capabilities['platformName']                    = 'Windows'
                Capabilities['appium:automationName']           = 'chromium'
                Capabilities['appium:newCommandTimeout']        = 2000
                app_config.Driver = appium.webdriver.Remote( AppiumServer, Capabilities )
                
        except BaseException as e:
            GetExceptionInfo(e)
            return None

        if app_config.Driver:
            app_config.Driver.implicitly_wait( 0 )
            print( 'app_config.Driver Initialization Complete' )
        
        return app_config.Driver != None
        ...

           
    def StartApp( self, StartURL ):

        self.StartURL   = StartURL

        print('Starting: ' + StartURL )
        
        try:
        
            app_config.Driver.get( StartURL )
            
            if app_config.Driver.title:
            
            
                StartPageActivity = self.WaitForPage()            
            
                StartPage = self.NewPage(
                            App = self,
                            PageName = TestApp.START_PAGE_KEY )
                    
                    
                if StartPage:
                    self.CurrentPage = str(app_config.Driver.current_url)
                    return StartPage
                else:
                    return False
                
            else:
                print('No current driver URL')
                self.ExitApp()
                return False
                
        except BaseException as e:
            GetExceptionInfo(e)
            self.ExitApp()
            return False
    
    
    # TODO: Make this accept any attribute of an element to waitfor
    def WaitForPage( self, WaitForCriteria = None):
        
        DriverActivity = None
        MaxCount       = 10
        Count          = 0
        
        self.Ready = False
        
        # wait for app activity/page to change
        while Count < MaxCount:

            Count += 1
            DriverActivity = str( app_config.Driver.current_url )
            
            print("DriverActivity  : "  + DriverActivity)
            print("CurrentActivity : "  + self.CurrentActivity)
            
            if DriverActivity == self.CurrentActivity:
                print(f"Waiting for DriverActivity to change. " +
                      f"Count = {Count}")
                time.sleep( 0.5 )
                
            else:
                print('DriverActivity has changed to: ' + DriverActivity)
                break
        
        if Count == MaxCount:
            print('DriverActivity did not change after waiting')
            return False
        
        # if caller did not ask to wait for anything else we're done
        if not WaitForCriteria:
            print('Setting CurrentActivity to: '+ DriverActivity)

            self.CurrentActivity        = DriverActivity
            app_config.CurrentActivity  = self.CurrentActivity
            
            return self.CurrentActivity
        
        # even if the activity/page has changed, it may not be
        # fully loaded and ready, so if the caller specifies a
        # resource-id of an element to wait for, then wait for it
        
        MaxCount    = 10
        Count       = 0
        
        while Count < MaxCount:
            
            Result = None
            Count += 1
            
            # create a temp element tree from the server DOM data
            # calls the @classmethod directly
            TempElementTree = app_pages.WebAppPage.CreateElementTree()
        
        
            if not (WaitForCriteria, True) in TempElementTree:
            
                print( f"Setting CurrentActivity to: {DriverActivity}")
                
                self.CurrentActivity        = DriverActivity
                app_config.CurrentActivity  = self.CurrentActivity
                
                return self.CurrentActivity
                
            else:
                print( f"Waiting for: {WaitForCriteria}, " +
                       f"Count = {Count}" )
                time.sleep(0.5)
        
        if Count == MaxCount:
            print(f"Could not find: {WaitForCriteria}")
            return False
...

        
...  # end of WebApp class


class AndroidApp( TestApp ):

    def __init__( self ):
        super().__init__( UseAppium = True )
        self.CurrentActivity = ''
        self.CurrentPage = None

    @classmethod
    def NewPage( cls, *args, **kwargs ):
                            
        print('Creating new AndroidAppPage')

        # intercept args and adjust if needed
        App         = kwargs['App']
        PageName    = kwargs['PageName']
        UniqueName  = None
        
        # check if the requested page already exists
        if hasattr(App, PageName):
        
            print("Page name collision")
            
            # append random string to requested page name
            UniqueName = PageName + '_' + RandomString(5)
            
            kwargs['PageName'] = UniqueName
            print('Renamed page to: ' + UniqueName)
        
        # try to make a new page
        NewPage = None
        NewPage = app_pages.AndroidAppPage( *args, **kwargs )
        
        if NewPage:
        
            print("Successfully created new page")
            print(f"Setting CurrentPage to: {NewPage.PageName}")
            
            setattr( App, NewPage.PageName, NewPage )
            App.CurrentPage             = NewPage
            app_config.CurrentPage      = NewPage
            return NewPage
            
        else:
            print("Failed to create new page")
            return False
        ...
        
        
    def InitializeDriver( self, UseAppium = True ):

        print('Initializing Appium app_config.Driver')
        
        try:
            Capabilities = {}
            Settings     = {}
            AppiumServer = 'http://127.0.0.1:4723'
            
            Capabilities['platformName']                = 'Android'
            Capabilities['appium:platformVersion']      = '13'
            Capabilities['appium:deviceName']           = 'emulator-5554'
            Capabilities['appium:automationName']       = 'uiautomator2'
            Capabilities['appium:nativeWebScreenshot']  = True
            Capabilities['appium:newCommandTimeout']    = 2000
            # Capabilities['appium:waitForIdleTimeout']       = 500
            # Capabilities['appium:waitForSelectorTimeout']   = 500
            # Capabilities['appium:scrollAcknowledgmentTimeout'] = 500
            # Capabilities['appium:actionAcknowledgmentTimeout']  = 500
            app_config.Driver = appium.webdriver.Remote( AppiumServer, Capabilities )
            
        except BaseException as e:
            GetExceptionInfo(e)
            return None

        if app_config.Driver:
            app_config.Driver.update_settings(Settings)
            app_config.Driver.implicitly_wait( 0 )
        
        return app_config.Driver != None
        ...    

    def StartApp(self, Package, Activity):

        self.Package   = Package
        self.Activity  = Activity

        print('Starting: ' + Package + ', ' + Activity)
        
        try:
        
            if not app_config.Driver.start_activity( Package, Activity ):
                print('Failed to Driver.start_activity')
                return False
            
            StartPageActivity = self.WaitForPage(
                                WaitForResourceId = 
                                "android:id/navigationBarBackground")
        
            if not StartPageActivity:
                print('Failed to wait for StartPage to be ready')
                return False
            
            StartPage = AndroidApp.NewPage(
                         App  = self,
                         PageName = StartPageActivity )
                
            if not StartPage:
                print('Failed to create StartPage')
                return False
            
            return StartPage
                
        except BaseException as e:
            GetExceptionInfo(e)
            return False
    
    
    # TODO: Make this accept any attribute of an element to waitfor
    def WaitForPage( self, WaitForResourceId = None):
        
        DriverActivity = None
        MaxCount       = 10
        Count          = 0
        
        self.Ready = False
        
        # wait for app activity/page to change
        while Count < MaxCount:

            Count += 1
            DriverActivity = str( app_config.Driver.current_activity )
            
            print("DriverActivity  : "  + DriverActivity)
            print("CurrentActivity : "  + self.CurrentActivity)
            
            if DriverActivity == self.CurrentActivity:
                print(f"Waiting for DriverActivity to change. " +
                      f"Count = {Count}")
                time.sleep( 0.5 )
                
            else:
                print('DriverActivity has changed to: ' + DriverActivity)
                break
        
        if Count == MaxCount:
            print('DriverActivity did not change after waiting')
            return False
        
        # if caller did not ask to wait for anything else we're done
        if not WaitForResourceId:
            print('Setting CurrentActivity to: '+ DriverActivity)

            self.CurrentActivity        = DriverActivity
            app_config.CurrentActivity  = self.CurrentActivity
            
            return self.CurrentActivity
        
        # even if the activity/page has changed, it may not be
        # fully loaded and ready, so if the caller specifies a
        # resource-id of an element to wait for, then wait for it
        
        MaxCount    = 10
        Count       = 0
        
        while Count < MaxCount:
            
            Result = None
            Count += 1
            
            # create a temp element tree from the server DOM data
            # calls the @classmethod directly
            TempElementTree = app_pages.AndroidAppPage.CreateElementTree()
        
            # search to find an element that exists 
            # with the targeted resource-id
            Result =  ([  Element
                          for Element in TempElementTree.Descendants()
                          if ( hasattr( Element, 'resource_id') 
                          and WaitForResourceId in Element.resource_id ) ])
            
            if Result:
                Result = Result[0]
                print( f"Found: {WaitForResourceId}, " +
                       f"In Node: {Result.ObjPath}" )
                       
                print( f"Setting CurrentActivity to: {DriverActivity}")
                
                self.CurrentActivity        = DriverActivity
                app_config.CurrentActivity  = self.CurrentActivity
                
                return self.CurrentActivity
                
            else:
                print( f"Waiting for: {WaitForResourceId}, " +
                       f"Count = {Count}" )
                time.sleep(0.5)
        
        if Count == MaxCount:
            print(f"Could not find: {WaitForResourceId}")
            return False
...


class HackerRankTest( WebApp ):

    def __init__( self, UseAppium = False ):
        super().__init__( UseAppium )
        self.TestAppURL = 'https://the-internet.herokuapp.com/dynamic_loading/1'
        #self.TestAppURL = 'http://the-internet.herokuapp.com/large'
    ...
    
    #  This basic test loads the web page, then:
    #  1.  Clicks the Start button.
    #  2.  Waits for the "Hello, World" hidden text to appear.
    #  3.  Refreshes the page
    #  4.  Rinse and repeat 50 times.
    
    def Test( self ):
            
        StartPage = self.StartApp( self.TestAppURL )
        
        if not StartPage:
            print('Failed to start app')
            self.ExitApp()
            return False

        for x in range(50):
       
            Button = None
            PageRootNode = None
            PageRootNode = app_config.CurrentPage.PageElementTree
            StartPage.PageSourceToFile()
            StartPage.EnumerateElementTree()
           
            # The framework builds a Python object tree from the HTML DOM.
            # Then I use List Comprehension to find elements
            
            Button = ([  Element
                         for Element in app_config.CurrentPage.PageElementTree.Descendants()
                         if Element.Name == 'button_0'
                         if Element.Text == 'Start'    ])[0]
            
            if Button:
                Button.Click()
            else:
                return False
            
            self.CurrentActivity = ''
            
            # Once the Start button is clicked, there is javascript on the
            # the web page that intentionally sleeps for 5-seconds before
            # making the "Hello, World" text visible.  So we wait for that.
            
            # Use another List Comprehension to wait for the element to appear.
            
            for x in range(10):
            
                TempElementTree = app_pages.WebAppPage.CreateElementTree()
                
                Button = ([ Element
                            for Element in TempElementTree.Descendants()
                            if      getattr(Element, 'id') == 'finish'
                            if not  getattr(Element, 'style' )])
                        
                if not Button:
                    time.sleep(1)

            # Refresh the page and do it again
            
            app_config.Driver.refresh()
            
            NewPageActivity = RandomString(20)     
            print('New Page/Activity: ' + NewPageActivity)
        
            NewPage = WebApp.NewPage( App = self,
                                      PageName = NewPageActivity )
                                
            if not NewPage:
                print('Failed to create new page: ' + NewPageActivity)
                self.ExitApp()
                return False            
    
            
        

class AndroidSettingsApp( AndroidApp ):

    def __init__( self ):
        super().__init__()
        self.SettingsAppPackage  = 'com.android.settings'
        self.SettingsAppActivity = 'com.android.settings.Settings'
    ...
    
    def ScrollToAllElementsTest( self,
                             ScrollElement,
                             RandomSelection = False, 
                             Reverse         = False,
                             Duration        = 250 ):

        if ScrollElement == None:
            return False
            
        ScrollingElements = ScrollElement.GetScrollingElements()

        ScrollingElementsIndexValues = [ Element.index
                                         for Element in ScrollingElements ]
                           
        SortedIndexValues            = sorted( ScrollingElementsIndexValues )
                                    
        SelectionList                = None
        
        if RandomSelection:
            SelectionList            = random.sample( 
                                        SortedIndexValues, 
                                        len( SortedIndexValues ))
        else:
            if Reverse:
                SelectionList        = reversed( SortedIndexValues )
            else:
                SelectionList        = SortedIndexValues
                                
        
        for SelectedIdx in SelectionList:
        
            SelectedElement = ScrollElement.GetScrollingElementByIndex(SelectedIdx)
            
            print('Selected Element: ' + 
                  SelectedElement.Name + ", Idx = " + str(SelectedIdx))
                            
            if not getattr(SelectedElement, 'displayed'):
            
                Result = ScrollElement.ScrollIntoViewByIndex( 
                         SelectedIdx, Duration = Duration)
            
                if not Result:
                    print('Error scrolling element into view')
                    return False
            #else:
            #    print('Selected Element is already visible')

            SelectedElement = ScrollElement.GetScrollingElementByIndex(SelectedIdx)
    
            if ScrollElement.IsPartialScrollingIndexElement( SelectedElement ):
                print("SELECTED ELEMENT IS A PARTIAL!")
                Pause()
            #else:
            #    print("Selected Element is not a partial")

            Focusable = SelectedElement.Attributes.get('focusable')
            if Focusable:
                if not SelectedElement.SetFocus( RepeatCount = 1, Duration = 50 ):
                    print('Error setting element focus')
                    Pause()
                    return False
            else:
                print("Selected item is not a focusable item")
            
                        
        return True
        
    ...    

    def TestSetup(self):
    
        ScrollElementKey     = 'ScrollElement'
        PageWaitForKey       = 'PageWaitFor'
        IndexParentPathKey   = 'IndexParentPath'
        ScrollingChildsKey   = 'ScrollingChildIDs'
        
        Pages = {}
        
        Pages[0] = {}
        Pages[0][ScrollElement]      = StartPage.Scrollable.ScrollView_1_0
        Pages[0][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[0][IndexParentPathKey] = 'LinearLayout_0.FrameLayout_1.LinearLayout_0.FrameLayout_0.RecyclerView_0'
        Pages[0][ScrollingChildIDs]  = ['android:id/icon', 'android:id/title', 'android:id/summary']

        Pages[1] = {}
        Pages[1][ScrollableElement]  = Page.Scrollable.RecyclerView_0_0
        Pages[1][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[1][IndexParentPathKey] = ''
        Pages[1][ScrollingChildIDs]  = ['android:id/title']

        Pages[2] = {}
        Pages[2][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[2][IndexParentPathKey] = 'LinearLayout_0.FrameLayout_1.LinearLayout_0.FrameLayout_0.RecyclerView_0'
        Pages[2][ScrollingChildIDs]  = ['android:id/icon', 'android:id/title', 'android:id/summary']

        Pages[3] = {}
        Pages[3][PageWaitForKey]     = 'com.android.settings:id/container_material'
        Pages[3][IndexParentPathKey] = 'LinearLayout_0.FrameLayout_1.LinearLayout_0.FrameLayout_0.RecyclerView_0'
        Pages[3][ScrollingChildIDs]  = ['android:id/icon', 'android:id/title', 'android:id/summary']


    
    def GuessScrollIndexParentElement( self, Page ):
    
        PageTreeRoot         = Page.PageElementTree
        
        ScrollViewElement    = None
        RecyclerViewElement  = None
        
        ScrollViewElement    = [ Element
                                 for Element in PageTreeRoot.Descendants()
                                 if Element.scrollable  == True
                                 if Element.focusable   == True 
                                 if 'ScrollView' in Element.Name
                                 if 'id/main_content_scrollable_container' in Element.resource_id ][0]
                            
        RecyclerViewElement = [ Element
                                for Element in ScrollViewElement.Descendants()
                                if Element.scrollable == False
                                if Element.focusable  == True
                                if 'RecyclerView' in Element.Name
                                if 'id/recycler_view' in Element.resource_id ][0]
        

        if  ScrollViewElement and RecyclerViewElement:
            return ScrollViewElement, RecyclerViewElement

        #  if not the above, then it might be this
        
        ScrollViewElement    = [ Element
                                 for Element in PageTreeRoot.Descendants()
                                 #if Element.scrollable  == True
                                 #if Element.focusable   == False 
                                 if 'ScrollView' in Element.Name
                                 if 'id/main_content_scrollable_container' in Element.resource_id ][0]
                            
        RecyclerViewElement = [ Element
                                for Element in ScrollViewElement.Descendants()
                                if Element.scrollable == True
                                if Element.focusable  == True
                                if 'RecyclerView' in Element.Name
                                if 'id/recycler_view' in Element.resource_id ][0]
        
        if  ScrollViewElement and RecyclerViewElement:
            return ScrollViewElement, RecyclerViewElement
            
        
    # @CheckMemory
    def Test(self):

        print("AndroidSettingsApp Test")
        
        StartPage = self.StartApp( self.SettingsAppPackage, 
                                   self.SettingsAppActivity )
        
        if not StartPage:
            print('Failed to start app')
            self.ExitApp()
            return False
        
        StartPageRootNode = StartPage.PageElementTree
        
        # MyListIterator = iter(MyList)
        # print(len(MyListIterator))
        # TypeError: object of type 'list_iterator' has no len()
        # if "abc" in MyListIterator: print("iterator: yes") 
        # else: print("iterator: no")
        # if "abc" in MyListIterator: print("iterator: yes") 
        # else: print("iterator: no")
        # if "abc" in MyList: print("list: yes")
        # else: print("list: no")
        # if "abc" in MyList: print("list: yes")
        # else: print("list: no")

                
        # Additional initializations for the StartPage
        # primary scroll container element
        StartPageScrollViewElement, StartPageRecyclerViewElement = (
            self.GuessScrollIndexParentElement( StartPage ))
        
        StartPageScrollingChildIDs = [ 'android:id/icon',
                                       'android:id/title', 
                                       'android:id/summary' ]
        
        print(StartPageRecyclerViewElement.Name)
        print(StartPageScrollViewElement.Name)
        
        StartPageScrollViewElement.Initialize( 
                                   StartPageRecyclerViewElement,
                                   StartPageScrollingChildIDs )
        
        
        ObjectTreeRoot = app_config.CurrentPage.PageElementTree
                
        AllNodes = ([   Element
                        for  Element  in  ObjectTreeRoot.Descendants() 
                    ])
        
        
        print('AllNodes Count: ', len( AllNodes ))
        Pause()
    

        ClickableNodes = ([
        
                            Element
                    
                            for  Element  in  ObjectTreeRoot.Descendants() 
                    
                            if   Element.clickable  ==  True
                    
                         ])


        print('ClickableNodes Count: ', len( ClickableNodes ))
        Pause()

    
        AllLeafNodeNamesAndPaths = (

                [( 
                
                    Element.Name, Element.ObjPath    ,)
              
                    for  Element  in  AllNodes
                    
                    if   len( Element.Descendants() ) == 0
                    
                ])


        print('AllLeafNodeNamesAndPaths Count: ', 
          len( AllLeafNodeNamesAndPaths ))
        
        Pause()

        
        AllAncestorsOfNodesHavingTextData = (
        
                [(
                
                    Parent.Name,    Child.text       ,)
              
                    for  Parent       in     AllNodes
                    for  Child        in     AllNodes
              
                    #if   Parent       in     Child.Ancestors() 
                    #if   Child.text   and    len( Child.text ) > 0
                  
                ])

        
        print('AllAncestorsOfNodesHavingTextData Count: ', 
          len( AllAncestorsOfNodesHavingTextData ))
        Pause()    
        
        
        DescendentsOfDescendants = (
        
                [(
                
                    GrandParent,  Parent,  Child     ,)
              
                    for   GrandParent    in    AllNodes
                    for   Parent         in    GrandParent.Descendants()
                    for   Child          in    Parent.Descendants()
 
                    #if   Parent          in    Child.Ancestors()
                    #if   GrandParent     in    Parent.Ancestors()
                ])


        print('DescendentsOfDescendants Count: ', 
          len( DescendentsOfDescendants ))
        
        Pause()
        
        

        
        

        # Discover all of the scrolling elements by scrolling through
        # the list and finding the non-visible items to include in the
        # page element tree
        
        
        Result = StartPageScrollViewElement.FindAllScrollingIndexElements(
                                            Duration = 350)
     
        match Result:
            case app_elements.ScrollableElement.SCROLL_RESULT_SCROLLED:
                print('SCROLL_RESULT_SCROLLED')
            case app_elements.ScrollableElement.SCROLL_RESULT_EOL:
                print('SCROLL_RESULT_EOL')
            case app_elements.ScrollableElement.SCROLL_RESULT_ERROR:
                print('Failed to FindAllScrollingIndexElements')
                print('SCROLL_RESULT_ERROR')
                self.ExitApp()
                return False
        
        '''
        for x in range(1):
            if not self.ScrollToAllElementsTest( 
                                     StartPageScrollable,
                                     Duration = 250,
                                     Reverse = True,
                                     RandomSelection = False):
                                     
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False

            if not self.ScrollToAllElementsTest( 
                             StartPageScrollable,
                             Duration = 250,
                             Reverse = False,
                             RandomSelection = False):
                             
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False
        '''
        
        StartPage.EnumerateElementTree()
        
        
        #StartPageSubPages = StartPageScrollable.GetScrollingElementIndexValues()
        
        self.ExitApp()
        return True
        
        for SubPageIndex in StartPageSubPages:
            
            
            #StartPage.EnumerateElementTree()
            #StartPage.PageSourceToFile()
            #StartPage.ElementTreeToFile()
        
            Pause()
            print("About to enter sub-page: " + str(SubPageIndex))
            Pause()
            
            if not StartPageScrollable.ScrollIntoViewByIndex( 
                                       SubPageIndex ):
                                                
                print('Failed to scroll into view: ' + str(SubPageIndex))
                self.ExitApp()
                return False
            
            ScrollingElement = StartPageScrollable.GetScrollingElementByIndex( 
                                                   SubPageIndex )
        
            if not ScrollingElement:
                print('Failed to get scrolling element')
                self.ExitApp()
                return False
                           
            # Tap on the scrolling element to load the sub-page
            if not ScrollingElement.Tap( Duration = 50 ):
                print('Failed to tap element')
                self.ExitApp()
                return False
        
            # A new page should load as a result of the Tap
            # wait for it to be ready
            NewPageActivity = self.WaitForPage(
                              "android:id/navigationBarBackground")

            if not NewPageActivity:
                print('Failed to wait for new page activity to start')
                self.ExitApp()
                return False
            
            print('New Page/Activity: ' + NewPageActivity)
        
            NewPage = AndroidApp.NewPage( App = self,
                                          Name = NewPageActivity )
                                
            if not NewPage:
                print('Failed to create new page: ' + NewPageActivity)
                self.ExitApp()
                return False
                
            #NewPage.PageSourceToFile()
            #NewPage.ElementTreeToFile()
        
            NewPageIndexParent, NewPageScrollable = self.GetScrollElementPair( NewPage )

            if not NewPageIndexParent or not NewPageScrollable:
                print('Could not locate IndexParentElement/PageScrollable pair')
                self.ExitApp()
                return False
            
            Pause()
            
            NewPageScrollable.Initialize( IndexParentElement = NewPageIndexParent,
                                          ScrollingChildIDs  = [ 'android:id/title' ] )
                    
            
            if not NewPageScrollable.FindAllScrollingIndexElements():
                print('Failed to FindAllScrollingIndexElements')
                self.ExitApp()
                return False
            
            Pause()
            
            if not self.ScrollToAllElementsTest( 
                             NewPageScrollable,
                             Duration = 250,
                             Reverse = True,
                             RandomSelection = False):
                             
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False

            if not self.ScrollToAllElementsTest( 
                             NewPageScrollable,
                             Duration = 250,
                             Reverse = False,
                             RandomSelection = False):
                             
                print('Failed to ScrollToAllElementsText')
                self.ExitApp()
                return False
        
            app_config.Driver.back()
            
        self.ExitApp()
        return True
    
...     # end of AndroidSettingsApp



if __name__ == '__main__':

    print('Hello, world')
    SettingsAppPackage  = 'com.android.settings'
    SettingsAppActivity = 'com.android.settings.Settings'
    
    
    #MyTestApp = AndroidSettingsApp() 
    #MyTestApp.Test()
    
    MyTestApp = HackerRankTest( UseAppium = False )
    
    MyTestApp.Test()


'''
[AndroidUiautomator2app_config.Driver@21de]   waitForIdleTimeout
[AndroidUiautomator2app_config.Driver@21de]   waitForSelectorTimeout
[AndroidUiautomator2app_config.Driver@21de]   scrollAcknowledgmentTimeout
[AndroidUiautomator2app_config.Driver@21de]   actionAcknowledgmentTimeout
[AndroidUiautomator2app_config.Driver@21de]   locationContextEnabled
[AndroidUiautomator2app_config.Driver@21de]   autoAcceptAlerts
[AndroidUiautomator2app_config.Driver@21de]   javascriptEnabled
[AndroidUiautomator2app_config.Driver@21de]   pageJavascriptEnabled
[AndroidUiautomator2app_config.Driver@21de]   handlesAlerts
[AndroidUiautomator2app_config.Driver@21de]   mobileEmulationEnabled
[AndroidUiautomator2app_config.Driver@21de]   cssSelectorsEnabled
[AndroidUiautomator2app_config.Driver@21de]   rotatable
[AndroidUiautomator2app_config.Driver@21de]   nativeEvents
[AndroidUiautomator2app_config.Driver@21de]   allowInvisibleElements
[AndroidUiautomator2app_config.Driver@21de]   ignoreUnimportantViews
[AndroidUiautomator2app_config.Driver@21de]   enableMultiWindows
[AndroidUiautomator2app_config.Driver@21de]   disableIdLocatorAutocompletion
[AndroidUiautomator2app_config.Driver@21de]   shouldUseCompactResponses
[AndroidUiautomator2app_config.Driver@21de]   trackScrollEvents
[AndroidUiautomator2app_config.Driver@21de]   disableAndroidWatchers
'''

'''
        #Capabilities['appium:browserName']         = 'Chrome'
        Capabilities['appium:waitForIdleTimeout']                   = 500
        Capabilities['appium:waitForSelectorTimeout']               = 500
        Capabilities['appium:scrollAcknowledgmentTimeout']          = 500
        Capabilities['appium:actionAcknowledgmentTimeout']          = 500
        Capabilities['appium:locationContextEnabled']               = True
        Capabilities['appium:autoGrantPermissions']                 = True
        Capabilities['appium:autoAcceptAlerts']                     = True
        Capabilities['appium:javascriptEnabled']                    = True
        Capabilities['appium:pageJavascriptEnabled']                = True
        Capabilities['appium:handlesAlerts']                        = True
        Capabilities['appium:mobileEmulationEnabled']               = False
        Capabilities['appium:cssSelectorsEnabled']                  = True
        Capabilities['appium:rotatable']                            = True
        Capabilities['appium:nativeEvents']                         = False
        Capabilities['appium:allowInvisibleElements']               = False
        Capabilities['appium:ignoreUnimportantViews']               = False
        Capabilities['appium:enableMultiWindows']                   = True
        Capabilities['appium:disableIdLocatorAutocompletion']       = True
        Capabilities['appium:shouldUseCompactResponses']            = False
        Capabilities['appium:unicodeKeyboard']                      = False
        Capabilities['appium:resetKeyboard']                        = False
        Capabilities['appium:trackScrollEvents']                    = True
        Capabilities['appium:disableAndroidWatchers']               = False
        Capabilities['appium:disableWindowAnimation']               = False
        Capabilities['appium:ignoreHiddenApiPolicyError']           = True
        Capabilities['appium:disableSuppressAccessibilityService']  = False
        Capabilities['appium:ensureWebviewsHavePages']              = False
        
        Settings['locationContextEnabled']                  = True
        Settings['disableWindowAnimation']                  = False
        Settings['disableAndroidWatchers']                  = False
        Settings['allowInvisibleElements']                  = False
        Settings['ignoreUnimportantViews']                  = False
        Settings['enableMultiWindows']                      = True
        Settings['disableIdLocatorAutocompletion']          = True
        Settings['shouldUseCompactResponses']               = False
        Settings['newCommandTimeout']                       = 1000
        Settings['waitForIdleTimeout']                      = 500
        Settings['waitForSelectorTimeout']                  = 500
        Settings['scrollAcknowledgmentTimeout']             = 500
        Settings['actionAcknowledgmentTimeout']             = 500
        Settings['disableSuppressAccessibilityService']     = True
        Settings['ignoreHiddenApiPolicyError']              = True
        Settings['trackScrollEvents']                       = True
        Settings['javascriptEnabled']                       = True
        Settings['pageJavascriptEnabled']                   = True
        Settings['handlesAlerts']                           = True
        Settings['mobileEmulationEnabled']                  = True
        Settings['cssSelectorsEnabled']                     = True
        Settings['rotatable']                               = True
        Settings['nativeEvents']                            = True
        Settings['autoAcceptAlerts']                        = True
   
        # Capabilities['appium:noSign'] = True
        # Capabilities['appium:appPackage']  =  'com.android.settings'
        # Capabilities['appium:appActivity'] =  'com.android.settings.Settings'
'''


'''
    def GetSubAppTitleElement(self, Title):
        
        def FindSubAppTitleElement(ElementObject = None, Title = Title):
            
            if ElementObject == None:
                ElementObject = self.SubAppRootNode
            
            if Title == 'Tips & support':
                if ElementObject.Selector == 'new UiSelector().resourceId("com.google.android.gms:id/gh_help_toolbar_text").className("android.view.ViewGroup").description("Help").index(1)':
                    print('FindSubAppTitleElement: Found SubAppTitleElement = ' + str(Title))
                    return ElementObject
            
            if 'class' in ElementObject.Attributes and 'content-desc' in ElementObject.Attributes:
                if ((ElementObject.Attributes['class'] == 'android.widget.FrameLayout') and
                    (ElementObject.Attributes['content-desc'] == str(Title))):
                        print('FindSubAppTitleElement: Found SubAppTitleElement = ' + str(Title))
                        return ElementObject
            
            for ChildObject in ElementObject:
                ElementResult = FindSubAppTitleElement(ChildObject, Title)
                if ElementResult != None:
                    return(ElementResult)
            return(None)
        
        while True:
            
            RootNode = self.CreateElementTree()
            # self.ElementTreeToFile(RootNode)
 
            SubAppTitleElement = FindSubAppTitleElement(
                                 ElementObject = RootNode, 
                                 Title = Title)
                                    
            if SubAppTitleElement != None:
                
                self.SubAppRootNode = RootNode
                
                if SubAppTitleElement.CreateInstance():
                    print('GetSubAppTitleElement: Located SubAppTitleElement: ' + str(Title))
                    return(SubAppTitleElement)
            
        return(None)    
    ...
    
         
    def GetSubAppNavigateUpOrBackElement(self):
    
        def FindSubAppNavigateUpOrBackElement(ElementObject = None):
            
            if ElementObject == None:
                ElementObject = self.SubAppRootNode
            
            if 'class' in ElementObject.Attributes and 'content-desc' in ElementObject.Attributes:
                if  ( ( ElementObject.Attributes['class'] == 'android.widget.ImageButton' ) and
                     ( (ElementObject.Attributes['content-desc'] == 'Navigate up') or
                       (ElementObject.Attributes['content-desc'] == 'Back') ) ):
                            print('FindSubAppNavigateUpOrBackElement: Found SubAppNavigateBackElement')
                            return ElementObject
            
            for ChildObject in ElementObject:
                ElementResult = FindSubAppNavigateUpOrBackElement(ChildObject)                
                if ElementResult != None:
                    return ElementResult
            return(None)
        
        while True:

            SubAppNavigateUpOrBackElement = FindSubAppNavigateUpOrBackElement(
                                            ElementObject = self.SubAppRootNode)
            
            if SubAppNavigateUpOrBackElement != None:
            
                #if SubAppNavigateUpOrBackElement.CreateInstance() ):
                #    print('GetSubAppNavigateUpOrBackElement: Located SubAppNavigateUpOrBackElement: ')
                return(SubAppNavigateUpOrBackElement)
                    
        return(None)                
    ...
'''
