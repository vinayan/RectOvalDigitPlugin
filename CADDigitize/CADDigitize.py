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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources_rc
import os.path


#Import own classes and tools
from CADDigitize_tools_circle import *
from CADDigitize_tools_rect import *
from CADDigitize_tools_ellipse import *
from CADDigitize_tools_arc import *
from CADDigitize_tools_regularpolygon import *
from CADDigitize_tools_modify import *
from CADDigitize_ND import CADDigitize_ND
from CADDigitize_dialog import Ui_CADDigitizeSettings

class CADDigitize:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CADDigitize_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):

        settings = QSettings()
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Add toolbar
        self.menu = QMenu()
        self.menu.setTitle( QCoreApplication.translate( "CADDigitize","&CADDigitize") )
        self.caddigitize_help = QAction( QCoreApplication.translate("CADDigitize", "Help"), self.iface.mainWindow() )
        self.caddigitize_settings = QAction( QCoreApplication.translate("CADDigitize", "Settings"), self.iface.mainWindow() )
        self.caddigitize_nd = QAction(QCoreApplication.translate("CADDigitize", "Numerical Digitize"), self.iface.mainWindow() )

        self.menu.addActions( [self.caddigitize_help, self.caddigitize_settings, self.caddigitize_nd] )

        menu_bar = self.iface.mainWindow().menuBar()
        actions = menu_bar.actions()
        lastAction = actions[ len( actions ) - 1 ]
        menu_bar.insertMenu( lastAction, self.menu )

        self.caddigitize_help.triggered.connect(self.doHelp)
        self.caddigitize_settings.triggered.connect(self.doSettings)
        self.caddigitize_nd.triggered.connect(self.doNumericalDigitize)
        self.caddigitize_nd.setEnabled(False)

        # Add button
        self.toolBar = self.iface.addToolBar("CADDigitize")
        self.toolBar.setObjectName("CADDigitize")

        self.optionsToolBar = self.iface.addToolBar("CADDigitize Options")
        self.optionsToolBar.setObjectName("CADDigitize Options")
        self.optionsToolBar.clear()

        self.circleToolButton = QToolButton(self.toolBar)
        self.rectToolButton = QToolButton(self.toolBar)
        self.ellipseToolButton = QToolButton(self.toolBar)
        self.arcToolButton = QToolButton(self.toolBar)
        self.rpolygonToolButton = QToolButton(self.toolBar)
        self.modifyToolButton = QToolButton(self.toolBar)
        self.circleToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.rectToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.ellipseToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.arcToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.rpolygonToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.modifyToolButton.setPopupMode(QToolButton.MenuButtonPopup)



        ###
        # Circles
        ###

        # Add actions
        self.circleBy2Points = QAction(QIcon(":/plugins/CADDigitize/icons/circleBy2Points.svg"),  QCoreApplication.translate( "CADDigitize","Circle by 2 points", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.circleBy3Points = QAction(QIcon(":/plugins/CADDigitize/icons/circleBy3Points.svg"),  QCoreApplication.translate( "CADDigitize","Circle by 3 points", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.circleByCenterRadius = QAction(QIcon(":/plugins/CADDigitize/icons/circleByCenterRadius.svg"),  QCoreApplication.translate( "CADDigitize","Circle by center and radius", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.circleByCenterPoint = QAction(QIcon(":/plugins/CADDigitize/icons/circleByCenterPoint.svg"),  QCoreApplication.translate( "CADDigitize","Circle by center and a point", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.circleBy2Tangents = QAction(QIcon(":/plugins/CADDigitize/icons/circleBy2Tangents.svg"),  QCoreApplication.translate( "CADDigitize","Circle by 2 tangents", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())

        self.circleToolButton.addActions( [ self.circleBy2Points, self.circleBy3Points, self.circleByCenterRadius, self.circleByCenterPoint, self.circleBy2Tangents ] )
        self.circleToolButton.setDefaultAction(self.circleBy2Points)
        self.toolBar.addWidget( self.circleToolButton )


        self.circleBy2Points.setCheckable(True)
        self.circleBy2Points.setEnabled(False)
        self.circleBy3Points.setCheckable(True)
        self.circleBy3Points.setEnabled(False)
        self.circleByCenterRadius.setCheckable(True)
        self.circleByCenterRadius.setEnabled(False)
        self.circleByCenterPoint.setCheckable(True)
        self.circleByCenterPoint.setEnabled(False)
        self.circleBy2Tangents.setCheckable(True)
        self.circleBy2Tangents.setEnabled(False)

        self.toolBar.addSeparator()

        ###
        # Rectangles
        ###

        self.rectBy3Points = QAction(QIcon(":/plugins/CADDigitize/icons/rectBy3Points.svg"), QCoreApplication.translate( "CADDigitize","Rectangle by 3 points", None, QApplication.UnicodeUTF8), self.iface.mainWindow())
        self.rectByExtent = QAction(QIcon(":/plugins/CADDigitize/icons/rectByExtent.svg"), QCoreApplication.translate( "CADDigitize","Rectangle by extent", None, QApplication.UnicodeUTF8), self.iface.mainWindow())
        self.rectFromCenter = QAction(QIcon(":/plugins/CADDigitize/icons/rectFromCenter.svg"), QCoreApplication.translate( "CADDigitize","Rectangle from center", None, QApplication.UnicodeUTF8), self.iface.mainWindow())
        self.squareFromCenter = QAction(QIcon(":/plugins/CADDigitize/icons/squareFromCenter.svg"), QCoreApplication.translate( "CADDigitize","Square from center", None, QApplication.UnicodeUTF8), self.iface.mainWindow())
        self.rectToolButton.addActions( [self.rectBy3Points, self.rectByExtent, self.rectFromCenter, self.squareFromCenter] )
        self.rectToolButton.setDefaultAction(self.rectBy3Points)
        self.toolBar.addWidget( self.rectToolButton )

        self.rectBy3Points.setEnabled(False)
        self.rectBy3Points.setCheckable(True)
        self.rectByExtent.setEnabled(False)
        self.rectByExtent.setCheckable(True)
        self.rectFromCenter.setEnabled(False)
        self.rectFromCenter.setCheckable(True)
        self.squareFromCenter.setEnabled(False)
        self.squareFromCenter.setCheckable(True)

        self.toolBar.addSeparator()

        ###
        # Ellipses
        ###


        # Add actions
        self.ellipseByCenter2Points = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByCenter2Points.svg"),  QCoreApplication.translate( "CADDigitize","Ellipse by center and 2 points", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.ellipseByCenter3Points = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByCenter3Points.svg"),  QCoreApplication.translate( "CADDigitize","Ellipse by center and 3 points", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.ellipseBy4Points= QAction(QIcon(":/plugins/CADDigitize/icons/ellipseBy4Points.svg"),  QCoreApplication.translate( "CADDigitize","Ellipse by 4 points", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.ellipseByFociPoint = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByFociPoint.svg"),  QCoreApplication.translate( "CADDigitize","Ellipse by foci and a point", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.ellipseFromCenter = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseFromCenter.svg"),  QCoreApplication.translate( "CADDigitize","Ellipse from center", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.ellipseByExtent = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByExtent.svg"),  QCoreApplication.translate( "CADDigitize","Ellipse by extent", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())

        self.ellipseToolButton.addActions( [ self.ellipseByCenter2Points, self.ellipseByFociPoint, self.ellipseFromCenter, self.ellipseByExtent ] )
        self.ellipseToolButton.setDefaultAction(self.ellipseByCenter2Points)
        self.toolBar.addWidget( self.ellipseToolButton )


        self.ellipseByCenter2Points.setCheckable(True)
        self.ellipseByCenter2Points.setEnabled(False)
        self.ellipseByCenter3Points.setCheckable(True)
        self.ellipseByCenter3Points.setEnabled(False)
        self.ellipseBy4Points.setCheckable(True)
        self.ellipseBy4Points.setEnabled(False)
        self.ellipseByFociPoint.setCheckable(True)
        self.ellipseByFociPoint.setEnabled(False)
        self.ellipseFromCenter.setCheckable(True)
        self.ellipseFromCenter.setEnabled(False)
        self.ellipseByExtent.setCheckable(True)
        self.ellipseByExtent.setEnabled(False)

        self.toolBar.addSeparator()

        ###
        # Arcs
        ###

        # Add actions
        self.arcByCenter2Points = QAction(QIcon(":/plugins/CADDigitize/icons/arcByCenter2Points.svg"),  QCoreApplication.translate( "CADDigitize","Arc by center and 2 points", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.arcBy3Points = QAction(QIcon(":/plugins/CADDigitize/icons/arcBy3Points.svg"),  QCoreApplication.translate( "CADDigitize","Arc by 3 points", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.arcByCenterPointAngle = QAction(QIcon(":/plugins/CADDigitize/icons/arcByCenterPointAngle.svg"),  QCoreApplication.translate( "CADDigitize","Arc by center, point and angle", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())

        self.arcToolButton.addActions( [ self.arcByCenter2Points, self.arcBy3Points, self.arcByCenterPointAngle ] )
        self.arcToolButton.setDefaultAction(self.arcByCenter2Points)
        self.toolBar.addWidget( self.arcToolButton )


        self.arcByCenter2Points.setCheckable(True)
        self.arcByCenter2Points.setEnabled(False)
        self.arcBy3Points.setCheckable(True)
        self.arcBy3Points.setEnabled(False)
        self.arcByCenterPointAngle.setCheckable(True)
        self.arcByCenterPointAngle.setEnabled(False)

        self.toolBar.addSeparator()


        ###
        # Regular Polygon
        ###

        self.rpolygonByCenterPoint = QAction(QIcon(":/plugins/CADDigitize/icons/rpolygonByCenterPoint.svg"),  QCoreApplication.translate( "CADDigitize","Regular polygon by center and point", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.rpolygonBy2Corners = QAction(QIcon(":/plugins/CADDigitize/icons/rpolygonBy2Corners.svg"),  QCoreApplication.translate( "CADDigitize","Regular polygon by 2 corners", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())

        self.rpolygonToolButton.addActions( [ self.rpolygonByCenterPoint, self.rpolygonBy2Corners ] )
        self.rpolygonToolButton.setDefaultAction(self.rpolygonByCenterPoint)
        self.toolBar.addWidget( self.rpolygonToolButton )

        self.rpolygonByCenterPoint.setCheckable(True)
        self.rpolygonByCenterPoint.setEnabled(False)
        self.rpolygonBy2Corners.setCheckable(True)
        self.rpolygonBy2Corners.setEnabled(False)

        self.toolBar.addSeparator()


        ###
        # Modify
        ###


        self.modifyTrimExtend = QAction(QIcon(":/plugins/CADDigitize/icons/modifyTrimExtend.svg"),  QCoreApplication.translate( "CADDigitize","Trim/Extend", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.modifyFillet = QAction(QIcon(":/plugins/CADDigitize/icons/modifyFillet.svg"),  QCoreApplication.translate( "CADDigitize","Fillet", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.modifyBevel = QAction(QIcon(":/plugins/CADDigitize/icons/modifyBevel.svg"),  QCoreApplication.translate( "CADDigitize","Bevel", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.modifyOffset = QAction(QIcon(":/plugins/CADDigitize/icons/modifyOffset.svg"),  QCoreApplication.translate( "CADDigitize","Offset", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())
        self.modifyRotation = QAction(QIcon(":/plugins/CADDigitize/icons/modifyRotation.svg"),  QCoreApplication.translate( "CADDigitize","Rotation", None, QApplication.UnicodeUTF8),  self.iface.mainWindow())

        self.modifyToolButton.addActions( [ self.modifyTrimExtend, self.modifyFillet, self.modifyBevel, self.modifyOffset] )
        self.modifyToolButton.setDefaultAction(self.modifyTrimExtend)
        self.toolBar.addWidget( self.modifyToolButton )

        self.modifyTrimExtend.setCheckable(True)
        self.modifyTrimExtend.setEnabled(False)
        self.modifyFillet.setCheckable(True)
        self.modifyFillet.setEnabled(False)
        self.modifyBevel.setCheckable(True)
        self.modifyBevel.setEnabled(False)
        self.modifyOffset.setCheckable(True)
        self.modifyOffset.setEnabled(False)
        self.modifyRotation.setCheckable(True)
        self.modifyRotation.setEnabled(False)

        ### Conect

        QObject.connect(self.circleBy2Points,  SIGNAL("activated()"), self.circleBy2PointsDigit)
        QObject.connect(self.circleBy3Points,  SIGNAL("activated()"), self.circleBy3PointsDigit)
        QObject.connect(self.circleByCenterRadius,  SIGNAL("activated()"),  self.circleByCenterRadiusDigit)
        QObject.connect(self.circleByCenterPoint,  SIGNAL("activated()"),  self.circleByCenterPointDigit)
        QObject.connect(self.circleBy2Tangents,  SIGNAL("activated()"), self.circleBy2TangentsDigit)
        QObject.connect(self.rectBy3Points,  SIGNAL("activated()"),  self.rectBy3PointsDigit)
        QObject.connect(self.rectByExtent,  SIGNAL("activated()"),  self.rectByExtentDigit)
        QObject.connect(self.rectFromCenter,  SIGNAL("activated()"),  self.rectFromCenterDigit)
        QObject.connect(self.squareFromCenter,  SIGNAL("activated()"),  self.squareFromCenterDigit)
        QObject.connect(self.ellipseByCenter2Points,  SIGNAL("activated()"), self.ellipseByCenter2PointsDigit)
        QObject.connect(self.ellipseByCenter3Points,  SIGNAL("activated()"), self.ellipseByCenter3PointsDigit)
        QObject.connect(self.ellipseBy4Points,  SIGNAL("activated()"),  self.ellipseBy4PointsDigit)
        QObject.connect(self.ellipseByFociPoint,  SIGNAL("activated()"),  self.ellipseByFociPointDigit)
        QObject.connect(self.ellipseFromCenter,  SIGNAL("activated()"),  self.ellipseFromCenterDigit)
        QObject.connect(self.ellipseByExtent,  SIGNAL("activated()"),  self.ellipseByExtentDigit)
        QObject.connect(self.arcByCenter2Points,  SIGNAL("activated()"), self.arcByCenter2PointsDigit)
        QObject.connect(self.arcBy3Points,  SIGNAL("activated()"), self.arcBy3PointsDigit)
        QObject.connect(self.arcByCenterPointAngle,  SIGNAL("activated()"), self.arcByCenterPointAngleDigit)
        QObject.connect(self.rpolygonByCenterPoint,  SIGNAL("activated()"), self.rpolygonByCenterPointDigit)
        QObject.connect(self.rpolygonBy2Corners,  SIGNAL("activated()"), self.rpolygonBy2CornersDigit)
        QObject.connect(self.modifyTrimExtend,  SIGNAL("activated()"), self.modifyTrimExtendDigit)
        QObject.connect(self.modifyFillet,  SIGNAL("activated()"), self.modifyFilletDigit)
        QObject.connect(self.modifyBevel,  SIGNAL("activated()"), self.modifyBevelDigit)
        QObject.connect(self.modifyOffset,  SIGNAL("activated()"), self.modifyOffsetDigit)
        QObject.connect(self.modifyRotation,  SIGNAL("activated()"), self.modifyRotationDigit)


        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)
        QObject.connect(self.canvas, SIGNAL("mapToolSet(QgsMapTool*)"), self.deactivate)



        # Get the tools
        self.circleBy2Points_tool = CircleBy2PointsTool( self.canvas )
        self.circleBy3Points_tool = CircleBy3PointsTool( self.canvas )
        self.circleByCenterRadius_tool = CircleByCenterRadiusTool( self.canvas )
        self.circleByCenterPoint_tool = CircleByCenterPointTool( self.canvas )
        self.circleBy2Tangents_tool = CircleBy2TangentsTool( self.canvas )
        self.rectBy3Points_tool = RectBy3PointsTool( self.canvas )
        self.rectByExtent_tool = RectByExtentTool( self.canvas )
        self.rectFromCenter_tool = RectFromCenterTool( self.canvas )
        self.squareFromCenter_tool = SquareFromCenterTool( self.canvas )
        self.ellipseByCenter2Points_tool = EllipseByCenter2PointsTool( self.canvas )
        self.ellipseByCenter3Points_tool = EllipseByCenter3PointsTool( self.canvas )
        self.ellipseBy4Points_tool= EllipseBy4PointsTool( self.canvas )
        self.ellipseByFociPoint_tool = EllipseByFociPointTool( self.canvas )
        self.ellipseByExtent_tool = EllipseByExtentTool( self.canvas )
        self.ellipseFromCenter_tool = EllipseFromCenterTool( self.canvas )
        self.arcByCenter2Points_tool = ArcByCenter2PointsTool( self.canvas )
        self.arcBy3Points_tool = ArcBy3PointsTool( self.canvas )
        self.arcByCenterPointAngle_tool = ArcByCenterPointAngleTool( self.canvas )
        self.rpolygonByCenterPoint_tool = RPolygonByCenterPointTool( self.canvas )
        self.rpolygonBy2Corners_tool = RPolygon2CornersTool( self.canvas )
        self.modifyTrimExtend_tool = ModifyTrimExtendTool( self.canvas )
        self.modifyFillet_tool = ModifyFilletTool( self.canvas )
        self.modifyBevel_tool = ModifyBevelTool( self.canvas )
        self.modifyOffset_tool = ModifyOffsetTool( self.canvas )
        self.modifyRotation_tool = ModifyRotationTool( self.canvas )

#####################################################################################################
#                                                                                                   #
#                                                                                                   #
#                                         FUNCTIONS                                                 #
#                                                                                                   #
#                                                                                                   #
#####################################################################################################

    def circleBy2PointsDigit(self):
        self.circleToolButton.setDefaultAction(self.circleBy2Points)
        self.canvas.setMapTool(self.circleBy2Points_tool)
        self.circleBy2Points.setChecked(True)
        QObject.connect(self.circleBy2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def circleBy3PointsDigit(self):
        self.circleToolButton.setDefaultAction(self.circleBy3Points)
        self.canvas.setMapTool(self.circleBy3Points_tool)
        self.circleBy3Points.setChecked(True)
        QObject.connect(self.circleBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def circleByCenterRadiusDigit(self):
        self.circleToolButton.setDefaultAction(self.circleByCenterRadius)
        self.canvas.setMapTool(self.circleByCenterRadius_tool)
        self.circleByCenterRadius.setChecked(True)
        QObject.connect(self.circleByCenterRadius_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def circleByCenterPointDigit(self):
        self.circleToolButton.setDefaultAction(self.circleByCenterPoint)
        self.canvas.setMapTool(self.circleByCenterPoint_tool)
        self.circleByCenterPoint.setChecked(True)
        QObject.connect(self.circleByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def circleBy2TangentsDigit(self):
        self.circleToolButton.setDefaultAction(self.circleBy2Tangents)
        self.canvas.setMapTool(self.circleBy2Tangents_tool)
        self.circleBy2Tangents.setChecked(True)
        QObject.connect(self.circleBy2Tangents_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def rectBy3PointsDigit(self):
        self.rectToolButton.setDefaultAction(self.rectBy3Points)
        self.canvas.setMapTool(self.rectBy3Points_tool)
        self.rectBy3Points.setChecked(True)
        QObject.connect(self.rectBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def rectByExtentDigit(self):
        self.rectToolButton.setDefaultAction(self.rectByExtent)
        self.canvas.setMapTool(self.rectByExtent_tool)
        self.rectByExtent.setChecked(True)
        QObject.connect(self.rectByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def rectFromCenterDigit(self):
        self.rectToolButton.setDefaultAction(self.rectFromCenter)
        self.canvas.setMapTool(self.rectFromCenter_tool)
        self.rectFromCenter.setChecked(True)
        QObject.connect(self.rectFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def squareFromCenterDigit(self):
        self.rectToolButton.setDefaultAction(self.squareFromCenter)
        self.canvas.setMapTool(self.squareFromCenter_tool)
        self.squareFromCenter.setChecked(True)
        QObject.connect(self.squareFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByCenter2PointsDigit(self):
        self.ellipseToolButton.setDefaultAction(self.ellipseByCenter2Points)
        self.canvas.setMapTool(self.ellipseByCenter2Points_tool)
        self.ellipseByCenter2Points.setChecked(True)
        QObject.connect(self.ellipseByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByCenter3PointsDigit(self):
        self.ellipseToolButton.setDefaultAction(self.ellipseByCenter3Points)
        self.canvas.setMapTool(self.ellipseByCenter3Points_tool)
        self.ellipseByCenter3Points.setChecked(True)
        QObject.connect(self.ellipseByCenter3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseBy4PointsDigit(self):
        self.ellipseToolButton.setDefaultAction(self.ellipseBy4Points)
        self.canvas.setMapTool(self.ellipseBy4Points_tool)
        self.ellipseBy4Points.setChecked(True)
        QObject.connect(self.ellipseBy4Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByFociPointDigit(self):
        self.ellipseToolButton.setDefaultAction(self.ellipseByFociPoint)
        self.canvas.setMapTool(self.ellipseByFociPoint_tool)
        self.ellipseByFociPoint.setChecked(True)
        QObject.connect(self.ellipseByFociPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseFromCenterDigit(self):
        self.ellipseToolButton.setDefaultAction(self.ellipseFromCenter)
        self.canvas.setMapTool(self.ellipseFromCenter_tool)
        self.ellipseFromCenter.setChecked(True)
        QObject.connect(self.ellipseFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByExtentDigit(self):
        self.ellipseToolButton.setDefaultAction(self.ellipseByExtent)
        self.canvas.setMapTool(self.ellipseByExtent_tool)
        self.ellipseByExtent.setChecked(True)
        QObject.connect(self.ellipseByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def arcByCenter2PointsDigit(self):
        self.arcToolButton.setDefaultAction(self.arcByCenter2Points)
        self.canvas.setMapTool(self.arcByCenter2Points_tool)
        self.arcByCenter2Points.setChecked(True)
        QObject.connect(self.arcByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)

    def arcBy3PointsDigit(self):
        self.arcToolButton.setDefaultAction(self.arcBy3Points)
        self.canvas.setMapTool(self.arcBy3Points_tool)
        self.arcBy3Points.setChecked(True)
        QObject.connect(self.arcBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)

    def arcByCenterPointAngleDigit(self):
        self.arcToolButton.setDefaultAction(self.arcByCenterPointAngle)
        self.canvas.setMapTool(self.arcByCenterPointAngle_tool)
        self.arcByCenterPointAngle.setChecked(True)
        QObject.connect(self.arcByCenterPointAngle_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)


    def rpolygonByCenterPointDigit(self):
        self.rpolygonToolButton.setDefaultAction(self.rpolygonByCenterPoint)
        self.canvas.setMapTool(self.rpolygonByCenterPoint_tool)
        self.rpolygonByCenterPoint.setChecked(True)
        QObject.connect(self.rpolygonByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def rpolygonBy2CornersDigit(self):
        self.rpolygonToolButton.setDefaultAction(self.rpolygonBy2Corners)
        self.canvas.setMapTool(self.rpolygonBy2Corners_tool)
        self.rpolygonBy2Corners.setChecked(True)
        QObject.connect(self.rpolygonBy2Corners_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

# MODIFY
    def modifyTrimExtendDigit(self):
        self.modifyToolButton.setDefaultAction(self.modifyTrimExtend)
        self.canvas.setMapTool(self.modifyTrimExtend_tool)
        self.modifyTrimExtend.setChecked(True)
        QObject.connect(self.modifyTrimExtend_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def modifyFilletDigit(self):
        self.modifyToolButton.setDefaultAction(self.modifyFillet)
        self.canvas.setMapTool(self.modifyFillet_tool)
        self.modifyFillet.setChecked(True)
        QObject.connect(self.modifyFillet_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def modifyBevelDigit(self):
        self.modifyToolButton.setDefaultAction(self.modifyBevel)
        self.canvas.setMapTool(self.modifyBevel_tool)
        self.modifyBevel.setChecked(True)
        QObject.connect(self.modifyBevel_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def modifyOffsetDigit(self):
        self.modifyToolButton.setDefaultAction(self.modifyOffset)
        self.canvas.setMapTool(self.modifyOffset_tool)
        self.modifyOffset.setChecked(True)
        QObject.connect(self.modifyOffset_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def modifyRotationDigit(self):
        self.modifyToolButton.setDefaultAction(self.modifyRotation)
        self.canvas.setMapTool(self.modifyRotation_tool)
        self.modifyRotation.setChecked(True)
        QObject.connect(self.modifyRotation_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)


    def doHelp(self):
        help_file = "file:///"+ self.plugin_dir + "/help/index.html"
        QDesktopServices.openUrl(QUrl(help_file))

    def doSettings(self):
        self.optionsToolBar.clear()
        self.settings = Ui_CADDigitizeSettings()
        self.settings.show()

    def doNumericalDigitize(self):
        mc = self.canvas
        layer = mc.currentLayer()

        self.nd = CADDigitize_ND(layer)
        self.nd.show()

    def toggle(self):
        self.optionsToolBar.clear()
        mc = self.canvas
        layer = mc.currentLayer()
        #Decide whether the plugin button/menu is enabled or disabled
        if layer <> None:
            if (layer.isEditable() and (layer.geometryType() == QGis.Polygon or layer.geometryType() == QGis.Line)):
                self.circleBy2Points.setEnabled(True)
                self.circleBy3Points.setEnabled(True)
                self.circleByCenterRadius.setEnabled(True)
                self.circleByCenterPoint.setEnabled(True)
                self.circleBy2Tangents.setEnabled(True)
                self.rectBy3Points.setEnabled(True)
                self.rectByExtent.setEnabled(True)
                self.rectFromCenter.setEnabled(True)
                self.squareFromCenter.setEnabled(True)
                self.ellipseByCenter2Points.setEnabled(True)
                self.ellipseByCenter3Points.setEnabled(True)
                self.ellipseBy4Points.setEnabled(True)
                self.ellipseByFociPoint.setEnabled(True)
                self.ellipseFromCenter.setEnabled(True)
                self.ellipseByExtent.setEnabled(True)
                self.arcByCenter2Points.setEnabled(True)
                self.arcBy3Points.setEnabled(True)
                self.arcByCenterPointAngle.setEnabled(True)
                self.rpolygonByCenterPoint.setEnabled(True)
                self.rpolygonBy2Corners.setEnabled(True)
                self.modifyTrimExtend.setEnabled(True)
                self.modifyFillet.setEnabled(True)
                self.modifyBevel.setEnabled(True)
                self.modifyOffset.setEnabled(True)
                self.modifyRotation.setEnabled(True)
                self.caddigitize_nd.setEnabled(True)

                QObject.connect(layer,SIGNAL("editingStopped()"),self.toggle)
                QObject.disconnect(layer,SIGNAL("editingStarted()"),self.toggle)
            else:
                self.circleBy2Points.setEnabled(False)
                self.circleBy3Points.setEnabled(False)
                self.circleByCenterRadius.setEnabled(False)
                self.circleByCenterPoint.setEnabled(False)
                self.circleBy2Tangents.setEnabled(False)
                self.rectBy3Points.setEnabled(False)
                self.rectByExtent.setEnabled(False)
                self.rectFromCenter.setEnabled(False)
                self.squareFromCenter.setEnabled(False)
                self.ellipseByCenter2Points.setEnabled(False)
                self.ellipseByCenter3Points.setEnabled(False)
                self.ellipseBy4Points.setEnabled(False)
                self.ellipseByFociPoint.setEnabled(False)
                self.ellipseFromCenter.setEnabled(False)
                self.ellipseByExtent.setEnabled(False)
                self.arcByCenter2Points.setEnabled(False)
                self.arcBy3Points.setEnabled(False)
                self.arcByCenterPointAngle.setEnabled(False)
                self.rpolygonByCenterPoint.setEnabled(False)
                self.rpolygonBy2Corners.setEnabled(False)
                self.modifyTrimExtend.setEnabled(False)
                self.modifyFillet.setEnabled(False)
                self.modifyBevel.setEnabled(False)
                self.modifyOffset.setEnabled(False)
                self.modifyRotation.setEnabled(False)
                self.caddigitize_nd.setEnabled(False)

                QObject.connect(layer,SIGNAL("editingStarted()"),self.toggle)
                QObject.disconnect(layer,SIGNAL("editingStopped()"),self.toggle)


    def deactivate(self):
        self.circleBy2Points.setChecked(False)
        self.circleBy3Points.setChecked(False)
        self.circleByCenterRadius.setChecked(False)
        self.circleByCenterPoint.setChecked(False)
        self.circleBy2Tangents.setChecked(False)
        self.rectBy3Points.setChecked(False)
        self.rectByExtent.setChecked(False)
        self.rectFromCenter.setChecked(False)
        self.squareFromCenter.setChecked(False)
        self.ellipseByCenter2Points.setChecked(False)
        self.ellipseByCenter3Points.setChecked(False)
        self.ellipseBy4Points.setChecked(False)
        self.ellipseByFociPoint.setChecked(False)
        self.ellipseFromCenter.setChecked(False)
        self.ellipseByExtent.setChecked(False)
        self.arcByCenter2Points.setChecked(False)
        self.arcBy3Points.setChecked(False)
        self.arcByCenterPointAngle.setChecked(False)
        self.rpolygonByCenterPoint.setChecked(False)
        self.rpolygonBy2Corners.setChecked(False)
        self.modifyTrimExtend.setChecked(False)
        self.modifyFillet.setChecked(False)
        self.modifyBevel.setChecked(False)
        self.modifyOffset.setChecked(False)
        self.modifyRotation.setChecked(False)

        QObject.disconnect(self.circleBy2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circleBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circleByCenterRadius_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circleByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circleBy2Tangents_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rectBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rectByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rectFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.squareFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByCenter3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseBy4Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByFociPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.arcByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)
        QObject.disconnect(self.arcBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)
        QObject.disconnect(self.arcByCenterPointAngle_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)
        QObject.disconnect(self.rpolygonByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rpolygonBy2Corners_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.modifyTrimExtend_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.modifyFillet_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.modifyBevel_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.modifyOffset_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.modifyRotation_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)


    def arcFeature(self, arc):
        geom = arc[0]
        center = arc[1]
        mc = self.canvas
        layer = mc.currentLayer()
        if layer.geometryType() == 2:
            arcPolygonSettings = QSettings()

            if arcPolygonSettings.value("/CADDigitize/arc/polygon","chord") == "pie":
                geom.insertVertex(center.x(), center.y(),0)

            geom = geom.convertToType(2, False)

        self.createFeature(geom)

    def createFeature(self, geom):
        settings = QSettings()
        mc = self.canvas
        layer = mc.currentLayer()
        renderer = mc.mapSettings()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        provider = layer.dataProvider()
        f = QgsFeature()


        #On the Fly reprojection.
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))

        # Line or Polygon
        if layer.geometryType() == 2:
            f.setGeometry(geom)
        else:
            f.setGeometry(geom.convertToType(1, geom.isMultipart()))

        # add attribute fields to feature
        fields = layer.pendingFields()

        # vector api change update
        f.initAttributes(fields.count())
        for i in range(fields.count()):
            f.setAttribute(i,provider.defaultValue(i))

        disable_attributes = settings.value( "/qgis/digitizing/disable_enter_attribute_values_dialog", False, type=bool)

        print disable_attributes

        dlg = None

        if disable_attributes:
            cancel = 1
        else:
            dlg = QgsAttributeDialog(layer, f, False)
            dlg.setIsAddDialog(True)
            if not dlg.dialog().exec_():
                cancel = 0
            else:
                layer.destroyEditCommand()
                cancel = 1

        print cancel
        if cancel == 1:
            if dlg:
                f.setAttributes(dlg.feature().attributes())
            layer.addFeature(f)
            layer.endEditCommand()

        mc.refresh()

    def changegeom(self, result):
        mc = self.canvas
        layer = mc.currentLayer()
        renderer = mc.mapRenderer()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        geom = result[0]
        fid = result[1]
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
        layer.beginEditCommand("Feature rotated")
        layer.changeGeometry( fid, geom )
        layer.endEditCommand()

    def unload(self):
        self.circleToolButton.removeAction(self.circleBy2Points)
        self.circleToolButton.removeAction(self.circleBy3Points)
        self.circleToolButton.removeAction(self.circleByCenterRadius)
        self.circleToolButton.removeAction(self.circleByCenterPoint)
        self.circleToolButton.removeAction(self.circleBy2Tangents)
        self.rectToolButton.removeAction(self.rectBy3Points)
        self.rectToolButton.removeAction(self.rectByExtent)
        self.rectToolButton.removeAction(self.rectFromCenter)
        self.rectToolButton.removeAction(self.squareFromCenter)
        self.ellipseToolButton.removeAction(self.ellipseByCenter2Points)
        self.ellipseToolButton.removeAction(self.ellipseByCenter3Points)
        self.ellipseToolButton.removeAction(self.ellipseBy4Points)
        self.ellipseToolButton.removeAction(self.ellipseByFociPoint)
        self.ellipseToolButton.removeAction(self.ellipseFromCenter)
        self.ellipseToolButton.removeAction(self.ellipseByExtent)
        self.arcToolButton.removeAction(self.arcByCenter2Points)
        self.arcToolButton.removeAction(self.arcBy3Points)
        self.arcToolButton.removeAction(self.arcByCenterPointAngle)
        self.rpolygonToolButton.removeAction(self.rpolygonByCenterPoint)
        self.rpolygonToolButton.removeAction(self.rpolygonBy2Corners)
        self.modifyToolButton.removeAction(self.modifyTrimExtend)
        self.modifyToolButton.removeAction(self.modifyFillet)
        self.modifyToolButton.removeAction(self.modifyBevel)
        self.modifyToolButton.removeAction(self.modifyOffset)
        self.modifyToolButton.removeAction(self.modifyRotation)
        self.optionsToolBar.clear()

        del self.circleToolButton
        del self.rectToolButton
        del self.ellipseToolButton
        del self.arcToolButton
        del self.rpolygonToolButton
        del self.modifyToolButton
        del self.toolBar
        del self.optionsToolBar
        del self.menu


