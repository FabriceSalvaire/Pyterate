.. include:: abbreviation.txt

.. _user-guide-page:

============
 User Guide
============

----------
 Commands
----------

The Python package installs two commands:

* pyterate-rst-api
* pyterate

To generate the API documentation, run

.. code-block:: sh

   pyterate-rst-api MyModule

To get help, use :code:`--help` option.

-------------------------
 Documentation Generator
-------------------------

The document generator has a similar purpose to that of a IPython notebook, but this one is based on
the concept of `literate programming <https://en.wikipedia.org/wiki/Literate_programming>`_.
Indeed, a document is a true Python file that can be executed, since additional contents like texts
or figures are embedded in comments.  Therefore, content is stored in a text file that can be easily
edited in a text editor, while a IPython notebook is a JSON file designed for a Web editor/viewer
application.  Both solutions can generate HTML files, but this one is more suited to generate a
static documentation, while a IPython Notebook allows to modify the content in live.  In fact, both
approaches are complementary.

The program *pyterate* walks recursively through a directory, *examples* by default,
and processes each Python file.  To skip a file, add :code:`#skip` at the first or second line of
the file.

A typical Python file contains these lines::

    # A source code comment
    #?# A comment that must not appear in the documentation

    python code ...

    #r# ==========================
    #r#  A Restructuredtext Title
    #r# ==========================

    python code ...

    #r#
    #r# Some reStructuredText contents
    #r#

    #m#
    #m# Some Markdown contents
    #m#
    #m# [An inline-style link](https://www.python.org)
    #m#

    python code ...

    # Insert the output of the following python code
    python code ...
    #o#

    # Hidden Python code
    #h# value = 123

    #r# Format RST content with current locals dictionary using @@<<@@...@@>>@@ instead of {...}.
    #r#
    #r# .. math::
    #r#
    #r#     I_d = @<@value@>@ I_s \left( e^{\frac{V_d}{n V_T}} - 1 \right)

    # Add Python code as a literal block
    #l# for x in ():
    #l#   1 / 0 / 0

    # Interactive code
    #<i#
    1 + 1
    2 * 4 * 2
    a, b = 1, 2
    1, 2, 3
    #i>#

    # Guarded error
    #<e#
    1/0
    #e>#

    # Add a Python file as a literal block
    #f# getthecode('RingModulator.py')

    # Add the file content as literal block
    #f# literal_include('kicad-pyspice-example.cir')

    # Insert an image
    #lfig# kicad-pyspice-example/kicad-pyspice-example.sch.svg

    # Insert Circuit_macros diagram
    #f# foo = circuit_macros
    #f# foo('circuit.m4')

    # Insert Tikz figure
    #f# width = 3 * 200
    #f# tikz('diode.tex',
    #f#       width=width)

    import matplotlib.pyplot as plt
    figure = plt.figure(1, (20, 10))

    # Insert a Matplotlib figure
    #f# save_figure('figure', 'my-figure.png',
    #f#             width=1280)
    #f#

    # Insert a table
    N = 2
    x = np.arange(-N, N, 0.5)
    y = np.arange(-N, N, 0.5)
    xx, yy = np.meshgrid(x, y, sparse=True)
    z = np.sin(xx**2 + yy**2) / (xx**2 + yy**2)
    #f# export('z', grid_size='x.shape[0]')
    #f# table(z, str_format='{:.1f}')
    #f# table('z', columns=[chr(ord('A') + i) for i in range(grid_size)], str_format='{:.3f}')

As you see it is a valid Python source code, but with some comments having a special meaning, so
called directive comments:

 * ``#?#`` is a comment that must not appear in the documentation,
 * ``#h#`` is a hidden Python code that must not appear in the documentation,
 * ``#r#`` is a reStructuredText content,
 * ``#m#`` is a Markdown content,
 * ``#o#`` instructs to include the sdtout of the previous Python code chunk,
 * ``#l#`` instructs to add Python code as a literal block,

The generator provides a more sophisticated way to embed computations in RST/Markdown documentation
using the Python string :func:`format` function. You just have to use the *@<@...@>@* syntax instead
of *{...}*, then the RST/Markdown string will be formatted using the current locals dictionary as
parameter to :func:`format`.  Note you can use hidden Python code to prepare data for this purpose.

You can get the effect of ``#o#`` for each line of a code block by surrounding the code with ``#<i#``
and ``#i>#``.

You can protect a code block against exceptions by surrounding the code with ``#<e#`` and ``#e>#``.

You can execute codes in the generator side with the special markup ``#f#``, this powerful feature
permits to extend Pyterate with custom codes.

The documentation generator will do these actions for each file:

 * read the source and collect the directive comments
 * generate a Restructuredtext ``.rst`` file
 * generate the Matplotlib figure is the file as a more recent timestamp than the rst file
 * generate a Circuit_macros figure if a m4 file as a more recent timestamp than the output image

At the end, the documentation generator generates a table of contents.
