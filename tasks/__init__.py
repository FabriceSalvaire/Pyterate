####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2019 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

# http://www.pyinvoke.org

####################################################################################################

from invoke import task, Collection
 # import sys

####################################################################################################

# PYSPICE_SOURCE_PATH = Path(__file__).resolve().parent

####################################################################################################

from . import clean
from . import doc
from . import git
from . import release
from . import anaconda

ns = Collection()
ns.add_collection(Collection.from_module(clean))
ns.add_collection(Collection.from_module(doc))
ns.add_collection(Collection.from_module(git))
ns.add_collection(Collection.from_module(release))
ns.add_collection(Collection.from_module(anaconda))
