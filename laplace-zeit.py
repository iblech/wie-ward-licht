#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import scipy.sparse
import scipy.sparse.linalg
import pygame
from pygame.locals import *
import matplotlib.pyplot as pl
import sys

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
            if i == 0 and breite/4 <= j <= 3*breite/4:
                b[hier] = 1
            elif j == 0 and hoehe/4 <= i <= 3*hoehe/4:
                b[hier] = -3
            else:
                b[hier] = -1
        else:
            A[hier, hier]   = -4/h**2
            A[hier, links]  =  1/h**2
            A[hier, oben]   =  1/h**2
            A[hier, unten]  =  1/h**2
            A[hier, rechts] =  1/h**2

            if i == int(hoehe/2) and j == int(breite/2):
                b[hier] = 0
            else:
                b[hier] = 0

# Lösung
A = A.tocsr()
print(A.todense())
x = scipy.sparse.linalg.spsolve(A, b)
print(x)

pygame.init()
px = 25
DISPLAYSURF = pygame.display.set_mode(((breite+1)*px, (hoehe+1)*px))
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GRAY  = (200, 200, 200)
clock = pygame.time.Clock()
pygame.display.set_caption("Knotenentwirrung")

#fig, ax = plt.subplots()
#heatmap = ax.pcolor(x.reshape((hoehe+1, breite+1)))
#plt.show()

def sigmoid(t): return 1/(1 + np.exp(-t))

def drawHeatmap(x):
    def scale(a,b,c,d): return (int(a*255), int(b*255), int(c*255))
    heatmap = pl.get_cmap()
    rows, cols = x.shape
    for i in range(rows):
        for j in range(cols):
            pygame.draw.rect(DISPLAYSURF, scale(*heatmap(sigmoid(x[i,j]))), (j*px, (hoehe-i)*px, px, px), 0)

speedup = 10
dt      = 0.1
userTime = 0
simulatedTime = 0
FPS = 10

def runPhysics(dt):
    global x
    x = x - dt * (b.reshape(N) - A.dot(x))

while True:
    userTime = userTime + clock.tick(FPS) * speedup / 1000
    print userTime

    while simulatedTime < userTime:
        runPhysics(dt)
        simulatedTime = simulatedTime + dt

    DISPLAYSURF.fill(WHITE)
    drawHeatmap(x.reshape((hoehe+1, breite+1)))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            j   = int(pos[0] / px)
            i   = hoehe - int(pos[1] / px)
            hier = i * (breite + 1) + j
            if event.button == 1:
                b[hier] = b[hier] + 0.5
            else:
                b[hier] = b[hier] - 0.5
