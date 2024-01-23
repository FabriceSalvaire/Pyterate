.. -*- Mode: rst -*-

.. include:: project-links.txt
.. include:: abbreviation.txt

==========
 Pyterate
==========

|Pypi License|
|Pypi Python Version|

|Pypi Version|

* Quick Link to `Production Branch <https://github.com/FabriceSalvaire/Pyterate/tree/master>`_
* Quick Link to `Devel Branch <https://github.com/FabriceSalvaire/Pyterate/tree/devel>`_

Overview
========

What is Pyterate ?
------------------

Pyterate is open source |Sphinx|_ add-ons which provide two tools for |Python|_ projects.  The
first one generates automatically the RST files for an API documentation based on the *autogen*
extension.  The second one provides a document generator based on the concept of literate
programming which can be used to make an example's based documentation.

Comparison to other libraries
-----------------------------

`Jupyter Book <https://jupyterbook.org>`_ does a similar job than Pyterate.
The main differences are:

* Jupyter Book is code cells in Markdown, while Pyterate is text cells in Python.
* Jupyter Book requires an editor plugin to handle a code cell. Actually only VS Studio is supported.
* But in all cases, we need an editor support.
* Jupyter Book exploits the recent Markdown support of Sphinx, thanks to MyST.
* Jupyter Book translates Markdown sources to Jupyter Notebooks and then execute them.
* Jupyter Book caches the executed notebooks.
* Jupyter Book use extensively the Sphinx API, while Pyterate just generates Rest sources, as well as Jupyter Notebooks.
* Pyterate uses a Jupyter kernel to execute the Python code.
* Pyterate can generate figures from external generators.
* Pyterate uses a "#" comment to prefix each line of a text cell. In practice it is very cumbersome. This is due to the lack of multi-line comment in Python, like C "/*...*/".  We could use '"""..."""' instead.  Such multi-line string is syntactical correct but do nothing.  They are only interpreted as docstring in some cases.

Python -> Pyterate -> ReST -> Sphinx -> HTML
Markdown MyST -> Sphinx[Jupyter Book] -> HTML

See also `Pweave <https://github.com/mpastell/Pweave>`_ a scientific report generator and a literate programming tool for Python. Pweave uses a similar approach to Jupyter Book. Pweave is **not maintained since 2019**.

Where is the Documentation ?
----------------------------

The documentation is available on the |PyterateHomePage|_.

What are the main features ?
----------------------------

The documentation generator features:

  * intermixing of code, text, `LaTeX formulae <https://www.mathjax.org>`_, figures and plots
  * use the `reStructuredText <https://en.wikipedia.org/wiki/ReStructuredText>`_ or `Markdown
    <https://en.wikipedia.org/wiki/Markdown>`_ syntax for text
  * use the |Sphinx|_ generator
  * embed computations in the text content
  * generation of circuit schematics using |Circuit_macros|_
  * generation of figures using |Tikz|_
  * generation of plots using |Matplotlib|_

How to install it ?
-------------------

Look at the `installation <https://fabricesalvaire.github.io/Pyterate/installation.html>`_ section in the documentation.

Credits
=======

Authors: `Fabrice Salvaire <http://fabrice-salvaire.fr>`_

News
====

.. include:: news.txt

.. End
