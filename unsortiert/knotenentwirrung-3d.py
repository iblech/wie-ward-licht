#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import pygame
import sys
from pygame.locals import *

FPS = 10

pygame.init()
DISPLAYSURF = pygame.display.set_mode((600, 600))
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GRAY  = (200, 200, 200)
clock = pygame.time.Clock()
pygame.display.set_caption("Knotenentwirrung")

bodies = []
numBodies = 30

for i in range(numBodies):
    phi = i / numBodies * 2 * np.pi
    bodies.append({
        "pos": np.array([np.sin(phi) + 2*np.sin(2*phi), np.cos(phi) - 2*np.cos(2*phi), -np.sin(3*phi)]),
        "vel": np.array([0.0, 0.0, 0.0])
    })

for i in range(1, 10):
    phi = i / 10 * 4 * np.pi
    bodies.append({
        "pos": np.array([np.cos(phi), -1 - 2 * phi, np.sin(phi)]),
        "vel": np.array([0.0, 0.0, 0.0])
    })

bodies[0]["pos"] = bodies[0]["pos"] + np.array([2.0, 0.0, 0.0])

def calcAcceleration(i):
    b = bodies[i]
    force = np.array([0.0, 0.0, 0.0])

#    for j in range(len(bodies)):
#        if i == j: continue
#        b_ = bodies[j]
#        r = b_["pos"] - b["pos"]
#        force = force - 5 * G / np.power(np.linalg.norm(r), 3) * r

    nextBody = bodies[(i + 1) % len(bodies)]
    prevBody = bodies[(i - 1) % len(bodies)]

    force = force - 10 * (2 * b["pos"] - prevBody["pos"] - nextBody["pos"])

    return force

# http://stackoverflow.com/a/18994296/4533618
def closestDistanceBetweenLines(a0,a1,b0,b1,clampAll=False,clampA0=False,clampA1=False,clampB0=False,clampB1=False):
    ''' Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
        Return distance, the two closest points, and their average
    '''

    # If clampAll=True, set all clamps to True
    if clampAll:
        clampA0=True
        clampA1=True
        clampB0=True
        clampB1=True

    # Calculate denomitator
    A = a1 - a0
    B = b1 - b0

    _A = A / np.linalg.norm(A)
    _B = B / np.linalg.norm(B)
    cross = np.cross(_A, _B);

    denom = np.linalg.norm(cross)**2


    # If denominator is 0, lines are parallel: Calculate distance with a projection
    # and evaluate clamp edge cases
    if (denom == 0):
        d0 = np.dot(_A,(b0-a0))
        d = np.linalg.norm(((d0*_A)+a0)-b0)

        # If clamping: the only time we'll get closest points will be when lines don't overlap at all.
        # Find if segments overlap using dot products.
        if clampA0 or clampA1 or clampB0 or clampB1:
            d1 = np.dot(_A,(b1-a0))

            # Is segment B before A?
            if d0 <= 0 >= d1:
                if clampA0 == True and clampB1 == True:
                    if np.absolute(d0) < np.absolute(d1):
                        return b0,a0,np.linalg.norm(b0-a0)
                    return b1,a0,np.linalg.norm(b1-a0)

            # Is segment B after A?
            elif d0 >= np.linalg.norm(A) <= d1:
                if clampA1 == True and clampB0 == True:
                    if np.absolute(d0) < np.absolute(d1):
                        return b0,a1,np.linalg.norm(b0-a1)
                    return b1,a1,np.linalg.norm(b1,a1)

        # If clamping is off, or segments overlapped, we have infinite results, just return position.
        return None,None,d



    # Lines criss-cross: Calculate the dereminent and return points
    t = (b0 - a0);
    det0 = np.linalg.det([t, _B, cross])
    det1 = np.linalg.det([t, _A, cross])

    t0 = det0/denom;
    t1 = det1/denom;

    pA = a0 + (_A * t0);
    pB = b0 + (_B * t1);

    # Clamp results to line segments if needed
    if clampA0 or clampA1 or clampB0 or clampB1:

        if t0 < 0 and clampA0:
            pA = a0
        elif t0 > np.linalg.norm(A) and clampA1:
            pA = a1

        if t1 < 0 and clampB0:
            pB = b0
        elif t1 > np.linalg.norm(B) and clampB1:
            pB = b1

    d = np.linalg.norm(pA-pB)

    return pA,pB,d

def dist(linkStart, linkEnd, linkStart_, linkEnd_):
    pA, pB, d = closestDistanceBetweenLines(linkStart, linkEnd, linkStart_, linkEnd_, clampAll=True)
    #r = distSlow(linkStart, linkEnd, linkStart_, linkEnd_)
    #print np.linalg.norm(pB - pA), np.linalg.norm(r)
    return pB - pA

def distSlow(linkStart, linkEnd, linkStart_, linkEnd_):
    rminNorm = None
    rmin     = None

    n = 4
    for mu in range(n):
        for tau in range(n):
            p = mu / n * linkStart + (1 - mu/n) * linkEnd
            q = tau / n * linkStart_ + (1 - tau/n) * linkEnd_
            r = q - p
            rNorm = np.linalg.norm(r)

            if rminNorm is None or rminNorm > rNorm:
                rminNorm = rNorm
                rmin     = r

    return r


def runPhysics(dt):
    acc = list(range(len(bodies)))

    for i in range(len(bodies)):
        acc[i] = calcAcceleration(i)

    for i in range(len(bodies)):
        linkStart = bodies[i]
        linkEnd   = bodies[(i + 1) % len(bodies)]

        for j in range(i):
            if j == (i + 1) % len(bodies) or j == i or j == (i - 1) % len(bodies): continue
            linkStart_ = bodies[j]
            linkEnd_   = bodies[(j + 1) % len(bodies)]

            r = dist(linkStart["pos"], linkEnd["pos"], linkStart_["pos"], linkEnd_["pos"])
            if np.linalg.norm(r) < 1e-10:
                print "*******"
                print i, j
            a = - 5 * G / np.power(np.linalg.norm(r), 3) * r

            acc[i] = acc[i] + a
            acc[(i + 1) % len(bodies)] = acc[(i + 1) % len(bodies)] + a
            acc[j] = acc[j] - a
            acc[(j + 1) % len(bodies)] = acc[(j + 1) % len(bodies)] - a

    for i in range(len(bodies)):
        b = bodies[i]
        b["pos"] = b["pos"] + dt * b["vel"]
        b["vel"] = b["vel"] + dt * acc[i]
        bodies[i]["vel"] = np.exp(-dt) * bodies[i]["vel"]

zoom  = { "value": 1.0, "delta": 0.0 }
angle = { "value": 0.0, "delta": 0.0 }

def toPlottingCoordinates(pos):
    scale = 200 / zoom["value"]
    x     =  np.cos(angle["value"]) * pos[0] + np.sin(angle["value"]) * pos[2]
    y     = pos[1]
    return (300 + int(x * scale), 300 - int(y * scale))

def drawKnot():
    pygame.draw.lines(DISPLAYSURF, (255,0,0), 1, [ toPlottingCoordinates(b["pos"]) for b in bodies ])
    for b in bodies:
        pygame.draw.circle(DISPLAYSURF, (0,0,0), toPlottingCoordinates(b["pos"]), np.max([1, 5 + int(b["pos"][2])]), 0)

    pygame.draw.lines(DISPLAYSURF, (200,200,200), 0, [ toPlottingCoordinates(b) for b in [[0,0,0], [1,0,0]] ])
    pygame.draw.lines(DISPLAYSURF, (200,200,200), 0, [ toPlottingCoordinates(b) for b in [[0,0,0], [0,1,0]] ])
    pygame.draw.lines(DISPLAYSURF, (200,200,200), 0, [ toPlottingCoordinates(b) for b in [[0,0,0], [0,0,1]] ])

simulatedTime = 0
userTime      = 0
speedup       = 0.1
dt            = 0.02
G             = 1

while True:
    userTime = userTime + clock.tick(FPS) * speedup / 1000
    print userTime / speedup

    while simulatedTime < userTime:
        runPhysics(dt)
        simulatedTime = simulatedTime + dt

    maxValue = np.max(np.abs([ b["pos"] for b in bodies ]))

    zoom["value"]  = zoom["value"] + (maxValue - zoom["value"]) / 1
    angle["value"] = angle["value"] + angle["delta"]
    angle["delta"] = 0.9 * angle["delta"]

    DISPLAYSURF.fill(WHITE)
    drawKnot()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_RIGHT]:
        angle["delta"] = 0.1
    elif pressed[pygame.K_LEFT]:
        angle["delta"] = -0.1
