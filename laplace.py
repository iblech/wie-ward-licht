#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import scipy.sparse
import scipy.sparse.linalg
import matplotlib.pyplot as plt

breite = 25
hoehe  = 20

h      = 1

# Gitter: von 0 bis breite eingeschlossen
N = (hoehe + 1) * (breite + 1)

A = scipy.sparse.lil_matrix((N, N))
b = np.zeros((N, 1))

# Gleichungen
for i in range(0,hoehe+1):
    for j in range(0,breite+1):
        hier   = i       * (breite + 1) + j
        links  = i       * (breite + 1) + (j - 1)
        oben   = (i + 1) * (breite + 1) + j
        rechts = i       * (breite + 1) + (j + 1)
        unten  = (i - 1) * (breite + 1) + j

        if i == 0 or j == 0 or i == hoehe or j == breite:
            A[hier, hier] = 1
            if i == 0:
                b[hier] = 1
            else:
                b[hier] = -1
        else:
            A[hier, hier]   = -4/h**2
            A[hier, links]  =  1/h**2
            A[hier, oben]   =  1/h**2
            A[hier, unten]  =  1/h**2
            A[hier, rechts] =  1/h**2

            if i == int(hoehe/2) and j == int(breite/2):
                b[hier] = 3
            else:
                b[hier] = 0

# Lösung
A = A.tocsr()
print(A.todense())
x = scipy.sparse.linalg.spsolve(A, b)
print(x)

fig, ax = plt.subplots()
heatmap = ax.pcolor(x.reshape((hoehe+1, breite+1)))
plt.show()
