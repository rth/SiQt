# SiQt

[![Build Status](https://travis-ci.org/rth/SiQt.svg?branch=master)](https://travis-ci.org/rth/SiQt)


A compatibility library for PyQt4, PyQt5 and PySide.


## Installation

 This package requires Python 2.7 or 3.2-3.5 with `six` and one of the following backends: `PyQt4`, `PySide`, `PyQt5`.

 It can be installed with, 
    
    pip install git+https://github.com/rth/SiQt.git


## Functionality

 SiQt provides several layers of abstraction to work with the existing Python Qt libraries.


#### 1. Aliasing
 
 The SiQt package will redirect imports to the active PyQt/PySide backend:

    import SiQt
    SiQt.use('PyQt4') 

    from SiQt import QtCore, Qt # or any other module that would be imported from PyQt4

#### 2. Imports interception

 With the `force=True` option, imports of PyQt4, PyQt5, PySide can be intercepted to load SiQt instead, which itself
redirects to the active PyQt/PySide backend:
  

    import SiQt
    SiQt.use('PyQt5', force=True)

    import PyQt4
    from PyQt4 import QtCore

    print(PyQt4.__name__)        # SiQt
    print(SiQt.backend)          # PyQt5
    print(QtCore.QT_VERSION_STR) # 5.5.1


#### 3. Compatibility layer

 By default, `SiQt.use` is called with the `mode='compatible'` argument, which attempts to compensate the differences in the API
 between backends. Alternatively, one can set `mode='strict'` to avoid this behaviour.

## Using from the command line
 
 SiQt can be directly used from the command line as follows,

    SIQT_BACKEND_FORCE='PySide' python -m SiQt my_pyqt4_gui.py

## Unit tests

 The unit tests suite can be run with
 
    python -c "from SiQt.siqt import tests; tests.run()"
