# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CADDigitize
                                 A QGIS plugin
 CAD like tools for QGis
 Fork of Rectangles Ovals Digitizing. Inspired by CadTools, LibreCAD/AutoCAD.
                              -------------------
        begin                : 2014-08-11
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Loïc BARTOLETTI
        email                : l.bartoletti@free.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *


class CircularArcOptions():
    
        def __init__(self, iface,  optionsToolBar):
            self.settings = QSettings()

            # Save reference to the QGIS interface
            self.iface = iface
            self.optionsToolBar = optionsToolBar
            
            self.optionsToolBar.clear()
            
            self.arc_featurePitch = self.settings.value("/CADDigitize/arc/pitch", 2,type=float)
            self.arc_featureAngle = self.settings.value("/CADDigitize/arc/angle", 1,type=int)
            self.arc_method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            self.arc_angleDirection = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
            self.arc_polygonCreation = self.settings.value("/CADDigitize/arc/polygon",  "pie")     
            
            
            ###
            # Options
            ###
            # Add featureSpin Pitch and Angle
#            number_group=QtGui.QButtonGroup(widget) # Number group
#            ArcFeaturePitch=QtGui.QRadioButton("pitch")
#            number_group.addButton(ArcFeaturePitch)
#            ArcFeatureAngle=QtGui.QRadioButton("angle")
#            number_group.addButton(ArcFeatureAngle)

            self.ArcFeatureSpin = QDoubleSpinBox(self.iface.mainWindow())

            if self.arc_method == "pitch":
#                self.radioFeaturePitch.setChecked(True)
#                self.radioFeatureAngle.setChecked(False)
                self.ArcFeatureSpin.setMinimum(1)
                self.ArcFeatureSpin.setMaximum(1000)
                self.ArcFeatureSpin.setDecimals(1)
                self.ArcFeatureSpin.setValue(self.arc_featurePitch)
            else:
#                self.radioFeaturePitch.setChecked(False)
#                self.radioFeatureAngle.setChecked(True)
                self.ArcFeatureSpin.setMinimum(1)
                self.ArcFeatureSpin.setMaximum(3600)
                self.ArcFeatureSpin.setDecimals(0)
                self.ArcFeatureSpin.setValue(self.arc_featureAngle)
            

            
            self.ArcFeatureSpinAction = self.optionsToolBar.addWidget(self.ArcFeatureSpin)
            self.ArcFeatureSpin.setToolTip("Number of segments")
            self.ArcFeatureSpinAction.setEnabled(True)
        
#            self.ArcFeatureSpin.valueChanged.connect(self.segmentsettingsArc)
            optionsToolBar.connect(self.ArcFeatureSpin, SIGNAL("valueChanged(float)"), self.segmentsettingsArc)
            
        def segmentsettingsArc(self):
            if self.arc_method == "pitch":
#                self.radioFeaturePitch.setChecked(True)
#                self.radioFeatureAngle.setChecked(False)
                self.settings.setValue("/CADDigitize/arc/segments", self.ArcFeatureSpin.value())
                self.settings.setValue("/CADDigitize/arc/pitch", self.ArcFeatureSpin.value())
            else:
#                self.radioFeaturePitch.setChecked(False)
#                self.radioFeatureAngle.setChecked(True)
                self.settings.setValue("/CADDigitize/arc/segments", int(self.ArcFeatureSpin.value()))
                self.settings.setValue("/CADDigitize/arc/angle", int(self.ArcFeatureSpin.value()))
                

