#-*- coding:utf-8 -*-

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QApplication

CADDigitize_functions = [
        # Circle
        QCoreApplication.translate( "CADDigitize","Circle by 2 points", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Circle by 3 points", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Circle by center and a point", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Circle by center and radius", None, QApplication.UnicodeUTF8),
        # Rectangle
        QCoreApplication.translate( "CADDigitize","Rectangle by 3 points", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Rectangle by extent", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Rectangle from center", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Square from center", None, QApplication.UnicodeUTF8),
        # Ellipse
        QCoreApplication.translate( "CADDigitize","Ellipse by center and 2 points", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Ellipse by extent", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Ellipse by foci and a point", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Ellipse from center", None, QApplication.UnicodeUTF8),
        # Arc
        QCoreApplication.translate( "CADDigitize","Arc by 3 points", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Arc by center and 2 points", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Arc by center and a point and angle", None, QApplication.UnicodeUTF8),
        # Regular polygon
        QCoreApplication.translate( "CADDigitize","Regular polygon by 2 corners", None, QApplication.UnicodeUTF8),
        QCoreApplication.translate( "CADDigitize","Regular polygon by center and a point", None, QApplication.UnicodeUTF8) ]


CADDigitize_functions_points = [
        #[Point, Point, Point, Option]
        # Circle
        [True, True, False, False],
        [True, True, True, False],
        [True, True, False, False],
        [True, True, False, "double"],
        # Rectangle
        [True, True, True, False],
        [True, True, False, False],
        [True, True, False, False],
        [True, True, False, False],
        # Ellipse
        [True, True, True, False],
        [True, True, False, False],
        [True, True, True, False],
        [True, True, False, False],
        # Arc
        [True, True, True, False],
        [True, True, True, False],
        [True, True, False, "angle"],
        # Regular polygon
        [True, True, False, False],
        [True, True, False, False]
        ]
