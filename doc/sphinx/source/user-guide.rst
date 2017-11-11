.. include:: abbreviation.txt

.. _user-guide-page:

============
 User Guide
============

----------
 Commands
----------

The Python package installs two commands:

* generate-rst-api
* generate-rst-examples

To generate the API documentation, run

.. code-block:: sh

   generate-rst-api MyModule

To get help, use :code:`--help` option.

-------------------------
 Documentation Generator
-------------------------

The document generator has a similar purpose than a IPython notebook, but it handles the generation
of circuit diagrams and static pages.

This tool walks recursively through the *examples* directory and processes each Python file.

A typical Python file contains these lines::

    # A source code comment
    #?# A comment that must not appear in the documentation

    python code ...

    #!# ==========================
    #!#  A Restructuredtext Title
    #!# ==========================

    python code ...

    #!#
    #!# Some reStructuredText contents
    #!#

    python code ...

    # Insert the output of the following python code
    python code ...
    #o#

    # Hidden Python code
    #h# value = 123

    #!# Format RST content with current locals dictionary using @@<<@@...@@>>@@ instead of {...}.
    #!#
    #!# .. math::
    #!#
    #!#     I_d = @<@value@>@ I_s \left( e^{\frac{V_d}{n V_T}} - 1 \right)

    # Add the file content as literal block
    #itxt# kicad-pyspice-example/kicad-pyspice-example.cir

    # Add a Python file as a literal block
    #i# RingModulator.py

    # Insert an image
    #lfig# kicad-pyspice-example/kicad-pyspice-example.sch.svg

    # Insert Circuit_macros diagram
    #cm# circuit.m4

    # Insert Tikz figure
    #tz# diode.tex

    # Insert a Matplotlib figure
    #fig# save_figure(figure, 'my-figure.png')

    python code ...

As you see it is a valid Python source code, but with some comments having a special meaning, so
called directive comments:

 * ``#?#`` is a comment that must not appear in the documentation,
 * ``#h#`` is a hidden Python code that must not appear in the documentation,
 * ``#!#`` is a reStructuredText content,
 * ``#o#`` instructs to include the sdtout of the previous Python code chunk,
 * ``#itxt#`` instructs to include the file content as a literal block,
 * ``#i#`` instructs to include a Python file as a literal block,
 * ``#lfig#`` instructs to include an image,
 * ``#cm#`` instructs to include a figure generated by the |Circuit_macros|_ diagram generator,
 * ``#tz#`` instructs to include a Tikz figure generated by pdflatex,
 * ``#fig#`` instructs to include a figure generated by Matplotlib and a
   modified version of the Python file including this uncommented line.

The generator provides a more sophisticated way to embed computations in the RST documentation using
the Python string :func:`format` function. You just have to use the *@<@...@>@* syntax instead of
*{...}*, then the RST string will be formatted using the current locals dictionary as parameter to
:func:`format`.  Note you can use hidden Python code to prepare data for this purpose.

The documentation generator will do these actions for each file:

 * read the source and collect the directive comments
 * generate a Restructuredtext ``.rst`` file
 * generate a Circuit_macros figure if a m4 file as a more recent timestamp than the output image
 * generate the Matplotlib figure is the file as a more recent timestamp than the rst file

At the end, the documentation generator generate a table of contents.