#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Numerische Simulation der Navier--Stokes-Gleichung wie in folgendem Artikel
# beschrieben:
#
#     Hans Johnston, Jian-Guo Liu.
#     Finite difference schemes for incompressible flow based on local pressure
#     boundary conditions.
#     Journal of Computational Physics 180, pages 120--154 (2002).
#
#     http://people.math.umass.edu/~johnston/PAPERS/JCP_1.pdf
#
# Projektarbeit von Alex, Jonas und Theo.

from __future__ import division
import numpy as np
import scipy.sparse
import scipy.sparse.linalg
import matplotlib.pyplot as plt

breite = 25  # y
laenge = 30  # x

h = 1                            # Maschenbreite
N = (laenge + 1) * (breite + 1)  # Gesamtzahl Gitterpunkte

nu = 1.0   # Viskosität
dt = 0.01  # Zeitschrittweite

u = np.zeros((laenge+1, breite+1, 2))  # Geschwindigkeitsvektorfeld
w = np.zeros((laenge+1, breite+1))     # Vortizität (ein Skalarfeld)

# Anfängliche Störung
u[10, 10, 0] =  100
u[10, 10, 1] =  200
u[25,  5, 0] = -200
u[25,  5, 1] =  200
u[25, 20, 1] = -200

# Initialisierung der Vortizität als w = Nabla x u
for i in range(laenge+1):
    for j in range(breite+1):
        if i == 0 or j == 0 or i == laenge or j == breite:
            w[i, j] = 0
        else:
            w[i, j] = ((u[i+1, j,1]-u[i-1, j,1])/(2*h))-((u[i, j+1,0]-u[i, j-1,0])/(2*h))

# Diskretisierung des Laplace-Operators
laplace = scipy.sparse.lil_matrix((N, N))
boundaryIndices = []
for i in range(0, laenge+1):  # i entspricht x-Koordinate
    for j in range(0, breite+1):  # j entspricht y
        index = i * (breite+1)+j

        if i == 0 or i == laenge or j == 0 or j == breite:
            laplace[index, index] = 1
            boundaryIndices.append(index)
        else:
            laplace[index, index] = -4/(h**2)
            laplace[index, index-1] = 1/(h**2)
            laplace[index, index+1] = 1/(h**2)
            laplace[index, index+breite+1] = 1/(h**2)
            laplace[index, index-breite-1] = 1/(h**2)

# Berechnet Delta f
def laplaceMult(f):
    res = np.zeros((laenge+1,breite+1))

    for i in range(laenge+1):
        for j in range(breite+1):
            if i == 0 or j == 0 or j == breite or i == laenge:
                res[i,j] = 0
            else:
                res[i,j] = (f[i,j+1]+f[i+1,j]+f[i,j-1]+f[i-1,j]-4*f[i,j])/h**2

    return res

# Berechnet (u * Nabla) f
def nabla_spezi(u,f):
    res=np.zeros((laenge+1,breite+1))

    for i in range(laenge+1):
        for j in range(breite+1):
            if i == 0 or j == 0 or j == breite or i == laenge:
                res[i,j] = 0
            else:
                res[i,j] = (u[i,j,0]*(f[i+1,j]-f[i-1,j])+u[i,j,1]*(f[i,j+1]-f[i,j-1]))/(2*h)

    return res

# Berechnet Nabla^perp f
def perpendicularToGradient(f):
    res = np.zeros((laenge+1, breite+1, 2))           

    for i in range(laenge+1):
        for j in range(breite+1):
            if i == 0 or j == 0 or i == laenge or j == breite:
                res[i, j, 0] = 0
                res[i, j, 1] = 0
            else:
                res[i, j, 0] = -(f[i, j+1]-f[i, j-1])/(2*h)
                res[i, j, 1] = +(f[i+1, j]-f[i-1, j])/(2*h)

    return res
 
def runphysics(omega, u):
    # Schritt 1 aus dem Artikel
    omega = omega + dt * (nu * laplaceMult(omega) - nabla_spezi(u,omega))

    # Schritt 2 aus dem Artikel
    b = omega.reshape((N,1))
    b[boundaryIndices] = 0
    psi = scipy.sparse.linalg.spsolve(laplace, b).reshape(laenge+1, breite+1)
    u = perpendicularToGradient(psi)

    # Schritt 3 aus dem Artikel
    for i in range(laenge+1):
        if i == 0:
            omega[i, 0]      = 2 * psi[1, 1]/(h**2)
            omega[i, breite] = 2 * psi[1, breite-1]/(h**2)
        elif i == laenge:
            omega[i, 0]      = 2 * psi[laenge-1, 1]/(h**2)
            omega[i, breite] = 2 * psi[laenge-1, breite-1]/(h**2)
        else:
            omega[i, 0]      = 2 * psi[i, 1]/(h**2)
            omega[i, breite] = 2 * psi[i, breite-1]/(h**2)

    for j in range(breite+1):
        if j == 0:
            omega[0, j]      = 2 * psi[1, 1]/(h**2)
            omega[laenge, j] = 2 * psi[laenge-1, 1]/(h**2)
        elif j == breite:
            omega[0, j]      = 2 * psi[1, breite-1]/(h**2)
            omega[laenge, j] = 2 * psi[laenge-1, breite-1]/(h**2)
        else:
            omega[0, j]      = 2 * psi[1, j]/(h**2)
            omega[laenge, j] = 2 * psi[laenge-1, j]/(h**2)

    return (omega, u, psi)

for it in range(1000):
    w, u, psi = runphysics(w, u)

    # Gefährlicher Hack, der dafür sorgen soll, dass über lange Zeit die
    # Energie nicht so schnell verloren geht
    w = 1.01 * w

    if it % 10 == 0:
        norms = np.sum(u**2,axis=-1)**0.5
        scale = np.max(norms)
        print "Iteration %s, größte Geschwindigkeit %f" % (it, scale)

        plt.clf()
        for k in range(1, 5):
            plt.subplot(2, 2, k).set_xlim([0, laenge])
            plt.subplot(2, 2, k).set_ylim([0, breite])
        plt.subplot(2, 2, 1).set_title(u"Vortizität")
        plt.subplot(2, 2, 2).set_title(u"Geschwindigkeitsbetrag")
        plt.subplot(2, 2, 3).set_title(u"Geschwindigkeit")
        plt.subplot(2, 2, 4).set_title(u"Stromfunktion")

        # Vortizität
        plt.subplot(2,2,1).pcolor(w.T)

        # Geschwindigkeitsbetrag
        plt.subplot(2,2,2).pcolor(norms.T)

        # Geschwindigkeit selbst
        ax = plt.subplot(2,2,3)
        for i in range(laenge+1):
            for j in range(breite+1):
                ax.arrow(i,j,u[i,j,0]/scale,u[i,j,1]/scale,head_width=0.1,head_length=0.1, fc='k', ec='k')

        # Stromfunktion
        ax = plt.subplot(2,2,4)
        ax.set_title(u"Stromfunktion")
        ax.contour(psi.T)

        # Für Ausgabe in Datei:
        #plt.savefig("image-%04d.png" % it)

        # Für Video:
        #plt.pause(0.2)

        # Für Einzelbilder:
        plt.show()
