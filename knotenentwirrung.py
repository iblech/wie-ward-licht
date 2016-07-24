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
numBodies = 10
for i in range(numBodies):
    phi = i / numBodies * 2 * np.pi
    bodies.append({
        "pos": np.array([np.cos(phi), np.sin(phi)]),
        "vel": np.array([0.0, 0.0])
    })
bodies[0]["pos"] = bodies[0]["pos"] + np.array([0.2, 0])

def calcAcceleration(i):
    b = bodies[i]
    force = np.array([0.0, 0.0])

    for j in range(len(bodies)):
        if i == j: continue
        b_ = bodies[j]
        r = b_["pos"] - b["pos"]
        force = force - G / np.power(np.linalg.norm(r), 3) * r

    nextBody = bodies[(i + 1) % len(bodies)]
    prevBody = bodies[(i - 1) % len(bodies)]

    force = force - 10 * (2 * b["pos"] - prevBody["pos"] - nextBody["pos"])

    return force

def runPhysics(dt):
    for i in range(len(bodies)):
        b = bodies[i]
        b["pos"] = b["pos"] + dt * b["vel"]
        acc = calcAcceleration(i)
        b["vel"] = b["vel"] + dt * acc

def toPlottingCoordinates(pos):
    scale = 200
    return (300 + int(pos[0] * scale), 300 - int(pos[1] * scale))

def drawKnot():
    pygame.draw.lines(DISPLAYSURF, (255,0,0), 1, [ toPlottingCoordinates(b["pos"]) for b in bodies ])
    for b in bodies:
        pygame.draw.circle(DISPLAYSURF, (0,0,0), toPlottingCoordinates(b["pos"]), 3, 0)

simulatedTime = 0
userTime      = 0
speedup       = 0.1
dt            = 0.01
G             = 1

while True:
    userTime = userTime + clock.tick(FPS) * speedup / 1000
    print userTime / speedup

    while simulatedTime < userTime:
        runPhysics(dt)
        simulatedTime = simulatedTime + dt

    DISPLAYSURF.fill(WHITE)
    drawKnot()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
