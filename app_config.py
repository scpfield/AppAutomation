import sys, os

Driver          = None
App             = None
CurrentPage     = None
CurrentActivity = None

# app_config.CurrentPage.PageElementTree

class Container():

    def __iter__( self ):
        #print("iter called")
        self._ChildList = []
        for Key, Value in self.__dict__.items():
            #print("iter key in self dict: " + Key)
            if 'Element' in Value.__class__.__name__:
                self._ChildList.append( Value )
        return self
        
    def __next__( self ):    
        #print("next called")
        if len( self._ChildList ) > 0:
            return self._ChildList.pop( 0 )
        else:
            del self._ChildList
            raise StopIteration
    
    def __len__( self ):
        #print("len called")
        Length = 0
        for Key, Value in self.__dict__.items():
            if 'Element' in Value.__class__.__name__:
                Length += 1
        return Length
        
    def __contains__( self, SubStr ):
        for Key, Value in self.__dict__.items():
            if SubStr in Key:
                return True
        return False
        
