.. include:: abbreviation.txt
.. include:: project-links.txt

.. raw:: html

    <style>
        .small-text {font-size: smaller}

	.spacer {height: 30px}

        .reduced-width {
	    max-width: 800px
        }

        .row {clear: both}

        @media only screen and (min-width: 1000px),
               only screen and (min-width: 500px) and (max-width: 768px){

            .column {
                padding-left: 5px;
                padding-right: 5px;
                float: left;
            }

            .column2  {
                width: 50%;
            }

            .column3  {
                width: 33.3%;
            }
        }
    </style>

.. raw:: html

   <div class="reduced-width">

############
 AutoSphinx
############

..
   image:: /_static/logo.png
   :alt: AutoSphinx logo
   :width: 750

********
Overview
********

AutoSphinx is free and open source (*) |Sphinx|_ add-ons which provide two tools for |Python|_
projects.  The first one provides a Sphinx source generator based on the concept of literate
programming which can be used to make an example's based documentation.  The second one is a tool
similar to `sphinx-apidoc <http://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_ to generate
automatically the Sphinx sources for an API documentation using the `autodoc extension
<http://www.sphinx-doc.org/en/master/ext/autodoc.html>`_.

.. a tool for automatic generation of Sphinx sources using the autodoc extension.

.. rst-class:: small-text

    (*) AutoSphinx is licensed under GPLv3 therms.

AutoSphinx requires Python 3 and works on Linux, Windows and OS X.

:ref:`To read more on AutoSphinx <overview-page>`

.. raw:: html

   <div class="spacer"></div>

.. rst-class:: clearfix row

.. rst-class:: column column2

:ref:`news-page`
================

What's changed in versions

.. rst-class:: column column2

:ref:`Installation-page`
========================

How to install AutoSphinx on your system

.. rst-class:: column column2

:ref:`user-faq-page`
====================

Answers to frequent questions

.. rst-class:: column column2

:ref:`examples-page`
====================

Document Generator Showcase

.. rst-class:: column column2

:ref:`user-guide-page`
======================

User manual to read first

.. rst-class:: column column2

:ref:`reference-manual-page`
============================

Technical reference material, for classes, methods, APIs, commands.

.. rst-class:: column column2

:ref:`development-page`
=======================

How to contribute to the project

.. rst-class:: column column2

:ref:`how-to-refer-page`
========================

Guidelines to cite AutoSphinx

.. rst-class:: column column2

..
    :ref:`donate-page`
    ==================

    If you want to donate to the project or need a more professional support.

.. raw:: html

   </div>

.. why here ???

.. rst-class:: clearfix row

.. raw:: html

   <div class="spacer"></div>

*******************
 Table of Contents
*******************

.. toctree::
  :maxdepth: 3
  :numbered:

  overview.rst
  news.rst
  installation.rst
  faq.rst
  user-guide.rst
  examples/index.rst
  design-notes.rst
  reference-manual.rst
  development.rst
  how-to-refer.rst

..
  roadmap.rst
  donate.rst
  related-projects.rst
  bibliography.rst
