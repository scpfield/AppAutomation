# AppAutomation
Python project that provides a framework for developing UI-driven automations with Selenium/Appium for WebApps and Android

Quite a lot is implemented, but still under construction.

The project wraps the Selenium / Appium APIs for both WebApps and Android, and provides a better workable and non-flakey framework to do things with, at least for my usage.   I have mostly been focusing on Android, but the WebApp stuff works too.  

There are 3 class hierarchies, paired together.

1)  Applications.  There is a base TestApp class, which is extended / inherited by WebApp, MobileApp, AndroidApp  (iOS some day).

2)  Pages/Activities.  These represent either HTML or Android XML  pages that users interact with.  They are abstracted into a Python Object Tree with all of the elements of the original pages, and wired to Selenium/Appium/etc. There is a base AppPage class, and extended by WebApp, AndroidApp pages for specifics.

3)  Elements.  These represent the UI controls on the pages.  Lots of types.  There is a base class and many subclasses that have different functionality depending on the type of element.  They are all Nodes of a Python object tree that each page manages.


