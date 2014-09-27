# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AdvancedDraw
                                 A QGIS plugin
 CAD like for circle, rectangle, ellipse
                             -------------------
        begin                : 2014-08-11
        copyright            : (C) 2014 by Loïc BARTOLETTI
        email                : l.bartoletti@free.fr
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load AdvancedDraw class from file AdvancedDraw.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .advanced_draw import AdvancedDraw
    return AdvancedDraw(iface)
