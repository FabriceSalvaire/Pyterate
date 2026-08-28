####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2020 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

from invoke import task

####################################################################################################

@task
def emacs_backup(ctx):
    ctx.run(r'find . -name "*~" -type f -exec rm -f {} \;')

@task(emacs_backup)
def clean(ctx):
    pass
