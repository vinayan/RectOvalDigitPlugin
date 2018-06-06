# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RectOvalDigit
                                 A QGIS plugin
 Rectangles, ovals digitizing tools
                             -------------------
        begin                : 2013-01-23
        copyright            : (C) 2013 by Pavol Kapusta
        email                : pavol.kapusta@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Rectangles Ovals Digitizing"


def description():
    return "Rectangles, ovals digitizing tools"


def version():
    return "Version 1.1.3"


def icon():
    return "icons/icon.png"


def qgisMinimumVersion():
    return "2.0"

def author():
    return "Pavol Kapusta"

def email():
    return "pavol.kapusta@gmail.com"

def classFactory(iface):
    # load RectOvalDigit class from file RectOvalDigit
    from rectovaldigit import RectOvalDigit
    return RectOvalDigit(iface)

