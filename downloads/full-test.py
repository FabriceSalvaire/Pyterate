# A source code comment
##
###
#?# A comment that must not appear in the documentation

foo = 1

#r# ==========================
#r#  A Restructuredtext Title
#r# ==========================

foo = 1

#r#
#r# Some reStructuredText contents
#r#

#m#
#m# Some Markdown contents
#m#
#m# [An inline-style link](https://www.python.org)
#m#

foo = 1

# Insert the output of the following python code
print(foo)
#o#

foo = 1

# Hidden Python code
#h# value = 123 * 3

foo = 1

#r# Format RST content with current locals dictionary using @@<<@@...@@>>@@ instead of {...}.
#r#
#r# .. math::
#r#
#r#     I_d = @<@value@>@ I_s \left( e^{\frac{V_d}{n V_T}} - 1 \right)

# Add Python code as a literal block
#l# for x in ():
#l#   1 / 0 / 0

# Intercative code
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
#f# image('kicad-pyspice-example.sch.svg')

# Insert Circuit_macros diagram
#f# foo = circuit_macros
#f# foo('circuit.m4')

# Insert Tikz figure
#f# width = 3 * 200
#f# tikz('diode.tex',
#f#       width=width)

import numpy as np
import matplotlib.pyplot as plt
figure = plt.figure(1, (20, 10))
x = np.arange(1, 10, .1)
y = np.sin(x)
plt.plot(x, y)

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

foo = 1
