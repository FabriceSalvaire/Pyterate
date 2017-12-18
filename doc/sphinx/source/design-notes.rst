.. _design-note-page:

==============
 Design Notes
==============

Genesis
-------

Pyterate started as a script tool to generate the documentation of the PySpice project, following
some experiments for an another project that I did one year before.  At this time, I had written
some real use cases of PySpice as Python scripts outputting and plotting results, and I was looking
for a way to associate texts and to freeze the output in the documentation generated using Sphinx.
One of the motivation was to have something better than comments in the code.  The idea is thus
similar to a IPython Notebook, i.e. glue codes, outputs, texts and figures all together, but the
document is a true Python file instead of a JSON document.  It means we can execute the file from
the console and we have a frozen version in the documentation.

Since the input document is a Python file, the textual contents must be embedded in comments.  Else
it would require a tool to split the code and the documentation, like in the Web language of Donald
Knuth.  The motivation is to do not break a Python linter implemented in an IDE like Emacs.
Consequently we only need a tool to capture the output and generate an rST file.  Originally the
tool used the "#!#" markup to indicate a rST content rather than a comment.

The original design was just a tool to "inverse" comment and code to a rST file, and the execution
of an instrumented version of the Python file to generate Matplolib figures and print delimiters in
the standard output so as to separate the output afterwards.

In fact the instrumented file is a kind of simple Jupyter kernel, but it encountered several
limitations, the delimiter mechanism is tricky, moreover we cannot retrieve the last result and
handle exceptions as in IPython.  The next step was thus to start using Jupyter to execute the code.
It is slower but much more powerful.

Another feature of the tool is the ability to generate figure using an external tool.  Such figures
are indicated using a markup, e.g. "#cm#" followed by the filename of the input file.  But it also
encountered an issue on the way to pass settings like the width of the figure in the HTML code.  rST
solves this issue using the directive syntax.  We can thus imagine to implement a similar feature
using a basic parser or even a full parser.  We can also use the Python parser to get an AST and
deal with it.

Since figures can be generated during the Sphinx process, we can argue this feature is not required
at all and we can simply use rST directives for this.  In fact this feature is mandatory, if we want
to generate a IPython Notebook since Sphinx cannot do it and is not designed for this task.
Moreover the writing of a Sphinx extension is not so easy.

The last feature implemented in the original tool was the ability to insert a computed value in the
rST content.  This feature was simply implemented as a string template and printed on the standard
output.

.. define generator = tool

.. paste old doc other markups ...

New Design
----------

A great force of TeX is due to the fact it is a programming language, i.e. we can embedded in the
text some programming logic.  This feature is interesting since we often present results in tables
and texts.

After some thought, I imagined a new design.

Textual contents in rST or Markdown are indicated using a dedicated markup, e.g. "#r#" and "#m#".
Occasionally these contents can act as string template which are rendered in the Jupyter kernel.  In
addition we have a "#l#" markup to indicate a literal Python block which is not executed and not
commented, this markup is just a shortcut to the corresponding rST directive.

Now the new concept is to replace all the figure markups by only one , "#f#", which indicate Python
codes that must be executed in the generator.  The purpose of this code is to instruct the generator
to do something like generate a figure using an external tool or execute a cell in the Jupyter
kernel to generate a figure using Matplolib.

We have thus now three types of contents, textual content, Python code executed in the Jupyter
kernel and Python code executed in the generator. That means we have now two Python layers that run
in parallel and we can pass data between them.

Technically, the "f" code is compiled and executed on the fly in the generator with a dedicated
globals and locals dictionary so as to isolate the execution.

This design is more verbose, but it solves all the issues of the first design.  For example, we can
now get result from the Jupyter kernel as a JSON string and use it later in a Jinja template to
render rST contents like a table or whatever.

Markdown versus rST
-------------------

The two markups languages are complementary.  Markdown is usually simpler than rST, but it lacks the
power of the roles and directives in rST.  We can extend Markdown but less easily than rST.

