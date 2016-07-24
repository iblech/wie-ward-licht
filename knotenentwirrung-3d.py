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
numBodies = 15

for i in range(numBodies):
    phi = i / numBodies * 2 * np.pi
    bodies.append({
        "pos": np.array([np.sin(phi) + 2*np.sin(2*phi), np.cos(phi) - 2*np.cos(2*phi), -np.sin(3*phi)]),
        "vel": np.array([0.0, 0.0, 0.0])
    })

#bodies[0]["pos"] = bodies[0]["pos"] + np.array([0.2, 0])

def calcAcceleration(i):
    b = bodies[i]
    force = np.array([0.0, 0.0, 0.0])

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

    for i in range(len(bodies)):
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
        pygame.draw.circle(DISPLAYSURF, (0,0,0), toPlottingCoordinates(b["pos"]), 3, 0)

    pygame.draw.lines(DISPLAYSURF, (200,200,200), 0, [ toPlottingCoordinates(b) for b in [[0,0,0], [1,0,0]] ])
    pygame.draw.lines(DISPLAYSURF, (200,200,200), 0, [ toPlottingCoordinates(b) for b in [[0,0,0], [0,1,0]] ])
    pygame.draw.lines(DISPLAYSURF, (200,200,200), 0, [ toPlottingCoordinates(b) for b in [[0,0,0], [0,0,1]] ])

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

    zoom["value"]  = zoom["value"] + (maxValue - zoom["value"]) / 1
    angle["value"] = angle["value"] + angle["delta"]
    angle["delta"] = 0.9 * angle["delta"]

    print zoom["value"], maxValue

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
