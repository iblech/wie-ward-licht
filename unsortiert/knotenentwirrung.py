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
numBodies = 5

for i in range(numBodies):
    phi = i / numBodies * np.pi
    bodies.append({
        "pos": np.array([np.cos(phi), 0.5 + np.sin(phi)]),
        "vel": np.array([0.0, 0.0])
    })

for i in range(numBodies):
    theta = i / numBodies
    bodies.append({
        "pos": (1 - theta) * np.array([-1.0, 0.5]) + theta * np.array([1.0, -0.5]),
        "vel": np.array([0.0, 0.0])
    })

for i in range(numBodies):
    phi = i / numBodies * np.pi
    bodies.append({
        "pos": np.array([np.cos(phi), -0.5 - np.sin(phi)]),
        "vel": np.array([0.0, 0.0])
    })

for i in range(1, numBodies - 1):
    theta = i / numBodies
    bodies.append({
        "pos": (1 - theta) * np.array([-1.0, -0.5]) + theta * np.array([1.0, 0.5]) + np.array([-0.1, 0]),
        "vel": np.array([0.0, 0.0])
    })

#bodies[0]["pos"] = bodies[0]["pos"] + np.array([0.2, 0])

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

zoom = { "value": 1.0, "delta": 0.0 }

def toPlottingCoordinates(pos):
    scale = 200 / zoom["value"]
    return (300 + int(pos[0] * scale), 300 - int(pos[1] * scale))

def drawKnot():
    pygame.draw.lines(DISPLAYSURF, (255,0,0), 1, [ toPlottingCoordinates(b["pos"]) for b in bodies ])
    for b in bodies:
        pygame.draw.circle(DISPLAYSURF, (0,0,0), toPlottingCoordinates(b["pos"]), 3, 0)

    box = [(1,1), (-1,1), (-1,-1), (1,-1)]
    pygame.draw.lines(DISPLAYSURF, (200,200,200), 1, [ toPlottingCoordinates(b) for b in box ])

simulatedTime = 0
userTime      = 0
speedup       = 0.1
dt            = 0.01
G             = 1

while True:
    userTime = userTime + clock.tick(FPS) * speedup / 1000

    while simulatedTime < userTime:
        runPhysics(dt)
        simulatedTime = simulatedTime + dt

    maxValue = np.max(np.abs([ b["pos"] for b in bodies ]))

#   zoom["delta"] = zoom["delta"] + (maxValue - zoom["value"]) / 1000
    zoom["value"] = zoom["value"] + (maxValue - zoom["value"]) / 1

    print zoom["value"], maxValue

    DISPLAYSURF.fill(WHITE)
    drawKnot()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
