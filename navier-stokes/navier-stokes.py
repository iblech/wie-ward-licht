#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Numerische Simulation der Navier--Stokes-Gleichung wie in folgendem Artikel
# beschrieben:
#
#     Hans Johnston, Jian-Guo Liu. Finite difference schemes for incompressible
#     flow based on local pressure boundary conditions. Journal of
#     Computational Physics 180, pages 120--154 (2002).
#
# Projektarbeit von Alex, Jonas und Theo.

from __future__ import division
import numpy as np
import scipy.sparse as ss
import scipy.sparse.linalg as ssl
import matplotlib.pyplot as plt
import math as m
import random

breite = 15  # y
laenge = 15  # x
faktor = 0   # Zoomfaktor

h = 1                            # Maschenbreite
N = (laenge + 1) * (breite + 1)  # Gesamtzahl Gitterpunkte

nu = 0.4   # Viskosität
dt = 0.01  # Zeitschrittweite

u = np.zeros((laenge+1, breite+1, 2))  # Geschwindigkeitsvektorfeld
w = np.zeros((laenge+1, breite+1))     # Vortizität (ein Skalarfeld)

laplace = ss.lil_matrix((N, N))  # Diskretisierung des Laplace-Operators
boundaryIndices = []
for i in range(0, laenge+1):  # i entspricht x_Koordinate
    for j in range(0, breite+1):  # j entspricht y
        index = i * (breite+1)+j

        if i==0 or i==laenge or j==0 or j==breite:
            laplace[index, index] = 1
            boundaryIndices.append(index)
        else:
            laplace[index, index] = -4/(h**2)
            laplace[index, index-1] = 1/(h**2)
            laplace[index, index+1] = 1/(h**2)
            laplace[index, index+breite+1] = 1/(h**2)
            laplace[index, index-breite-1] = 1/(h**2)

#innere Punkte
def laplaceMult(f):
    laplaceM=np.zeros((laenge+1,breite+1))
    for i in range(laenge+1):
        for j in range(breite+1):
            if i==0 or j==0 or j==breite or i==laenge:
                laplaceM[i,j]=0
            else:
                laplaceM[i,j]=(f[i,j+1]+f[i+1,j]+f[i,j-1]+f[i-1,j]-4*f[i,j])/h**2
                
    return laplaceM

def nabla_spezi(u,f):
    Result=np.zeros((laenge+1,breite+1))
    for i in range(laenge+1):
        for j in range(breite+1):
            if i==0 or j==0 or j==breite or i==laenge:
                Result[i,j]=0
            else:
                Result[i,j]=(u[i,j,0]*(f[i+1,j]-f[i-1,j])+u[i,j,1]*(f[i,j+1]-f[i,j-1]))/(2*h)
    return Result   

def perpendicularToGradient(f):
    res = np.zeros((laenge+1, breite+1, 2))           

    for i in range(laenge+1):
        for j in range(breite+1):
            if i==0 or j==0 or i==laenge or j==breite:
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
    psi = ssl.spsolve(laplace, b).reshape(laenge+1, breite+1)
    u = perpendicularToGradient(psi)

    # Schritt 3 aus dem Artikel
    for i in range(laenge+1):
        if i==0:
            omega[i, 0]      = 2*psi[1, 1]/(h**2)
            omega[i, breite] = 2*psi[1, breite-1]/(h**2)
        elif i==laenge:
            omega[i, 0]      = 2*psi[laenge-1, 1]/(h**2)
            omega[i, breite] = 2*psi[laenge-1, breite-1]/(h**2)
        else:
            omega[i, 0]      = 2*psi[i, 1]/(h**2)
            omega[i, breite] = 2*psi[i, breite-1]/(h**2)

    for j in range(breite+1):
        if j==0:
            omega[0, j]      = 2*psi[1, 1]/(h**2)
            omega[laenge, j] = 2*psi[laenge-1, 1]/(h**2)
        elif j==breite:
            omega[0, j]      = 2*psi[1, breite-1]/(h**2)
            omega[laenge, j] = 2*psi[laenge-1, breite-1]/(h**2)
        else:
            omega[0, j]      = 2*psi[1, j]/(h**2)
            omega[laenge, j] = 2*psi[laenge-1, j]/(h**2)

    return (omega, u)
    
def init():
    # hier geschwindigkeit angeben
    u[10, 10, 0]=100
    u[10, 10, 1]=200

    for i in range(laenge+1):
        for j in range(breite+1):
            if i==0 or j==0 or i==laenge or j==breite:
                w[i, j]=0
            else:
                w[i, j]=((u[i+1, j,1]-u[i-1, j,1])/(2*h))-((u[i, j+1,0]-u[i, j-1,0])/(2*h))

# Zeichenfunktion
def paint_AVG(u):
    betrag=0.7*h
    
    
    bts=0      
    for i in range(laenge+1):
        for j in range(breite+1):
            ebt=m.sqrt(u[i,j,0]**2+u[i,j,1]**2)
            bts+=ebt
    avg=bts/((laenge+1)*(breite+1))
    if avg!=0:
        faktor=betrag/avg
    else:
        faktor=1
    
    
    
    #Plotting    
    ax=plt.axes()
    ax.set_xlim([0,breite])
    ax.set_ylim([0,laenge])
    for i in range(laenge+1):
        for j in range(breite+1):
            ax.arrow(i,j,u[i,j,0]*faktor,u[i,j,1]*faktor,head_width=0.1,head_length=0.1, fc='k', ec='k')
    plt.show()
    
# Zeichenfunktion 2
def paint_MAX(u):
    global faktor
    if faktor==0 or True:
        betrag=0.7*h
        
        
        maximum=0
        for i in range(laenge+1):
            for j in range(breite+1):
                ebt=m.sqrt(u[i,j,0]**2+u[i,j,1]**2)
                if ebt>maximum:
                    maximum=ebt
                    
        if maximum!=0:
            faktor=betrag/maximum
        else:
            faktor=1
        print maximum
    
    
    #Plotting    
    ax=plt.axes()
    ax.set_xlim([0,laenge])
    ax.set_ylim([0,breite])
    for i in range(laenge+1):
        for j in range(breite+1):
            ax.arrow(i,j,u[i,j,0]*faktor,u[i,j,1]*faktor,head_width=0.1,head_length=0.1, fc='k', ec='k')
            
    plt.show()

def paintSkalar(f):
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(f)
    plt.show()
    
    
def paintSkalarAbs(f):
    
    fig, ax = plt.subplots()
    absskalar=np.zeros((laenge+1, breite+1))
    for i in range(laenge+1):
        for j in range(breite+1):
            absskalar[i, j]=abs(f[i, j])
    heatmap = ax.pcolor(absskalar)
    plt.show()
    
def paintVektorAbs(u):
    fig, ax = plt.subplots()
    skalar=np.zeros((laenge+1, breite+1))
    for i in range(laenge+1):
        for j in range(breite+1):
            skalar[i, j]=m.sqrt(u[i, j, 0]**2+u[i, j, 1]**2)
    heatmap = ax.pcolor(skalar)
    plt.show()
            
init()

for i in range(1000):
    w, u = runphysics(w, u)
    if i%10==0:
        print "Iteration %s"%(i)
        print "Rotation"
        paintSkalar(w)
        print "Rotation (Betrag)"
        paintSkalarAbs(w)
        print "Geschwindigkeit (Betrag)"
        paintVektorAbs(u)
        print "Vektorfeld"
        paint_MAX(u)
