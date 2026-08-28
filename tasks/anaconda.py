####################################################################################################
#
# Pyterate - Sphinx add-ons to create API documentation for Python projects
# Copyright (C) 2020 Fabrice Salvaire
# SPDX-License-Identifier: GPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from pathlib import Path
import shutil

from invoke import task

####################################################################################################

# enable anaconda environment
#   source .../miniconda3/bin/activate

@task()
def conda_build(ctx):
    with ctx.cd('anaconda'):
        ctx.run('conda build .')
        # ctx.run('conda build purge')

@task()
def conda_login(ctx):
    with open('.anaconda-login.txt') as fh:
        username = fh.readline().strip()
        password = fh.readline().strip()
    print('"{}" "{}"'.format(username, password))
    ctx.run('anaconda login --username="{}" --password="{}"'.format(username, password))

@task(conda_build, conda_login)
def conda_upload(ctx):
    result = ctx.run('conda build . --output')
    path = str(result.stdout).strip()
    ctx.run('anaconda upload {}'.format(path))
