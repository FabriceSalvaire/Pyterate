####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2020 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from invoke import task

####################################################################################################

@task
def flycheck(ctx):
    with ctx.cd(ctx.Package):
        ctx.run(r'find . -name "flycheck*.py" -exec rm {} \;')

@task
def emacs_backup(ctx):
    ctx.run(r'find . -name "*~" -type f -exec rm -f {} \;')

@task(flycheck, emacs_backup)
def clean(ctx):
    pass
