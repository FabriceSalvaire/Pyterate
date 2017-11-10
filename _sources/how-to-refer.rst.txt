.. _how-to-refer-page:

===========================
 How to Refer to AutoSphinx ?
===========================

Up to now, the official url for AutoSphinx is @project_url@

*A permanent redirection will be implemented if the domain change in the future.*

On Github, you can use the **AutoSphinx** `topic <https://github.com/search?q=topic%3AAutoSphinx&type=Repositories>`_ for repository related to AutoSphinx.

A typical `BibTeX <https://en.wikipedia.org/wiki/BibTeX>`_ citation would be, for example:

.. code:: bibtex

    @software{AutoSphinx,
      author = {Fabrice Salvaire}, % actual author and maintainer
      title = {AutoSphinx},
      url = {@project_url@},
      version = {x.y},
      date = {yyyy-mm-dd}, % set to the release date
    }

    @Misc{AutoSphinx,
      author = {Fabrice Salvaire},
      title = {AutoSphinx},
      howpublished = {\url{@project_url@}},
      year = {yyyy}
    }
