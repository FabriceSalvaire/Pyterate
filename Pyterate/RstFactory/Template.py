####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

# Fixme: harcoded !!!
INCLUDES_TEMPLATE = """
.. include:: /project-links.txt
.. include:: /abbreviation.txt
"""

TITLE_TEMPLATE = """
{title_line}
 {title}
{title_line}

"""

TOC_TEMPLATE = """

.. toctree::
  :maxdepth: 1

"""

GET_CODE_TEMPLATE = """
.. getthecode:: {filename}
    :language: python

"""
