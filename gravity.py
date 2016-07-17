#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import pygame
import sys
from pygame.locals import *

FPS = 15

pygame.init()
DISPLAYSURF = pygame.display.set_mode((800, 600))
WHITE = (255, 255, 255)
clock = pygame.time.Clock()
pygame.display.set_caption("Gravitation")

bodies = {
    "earth": {
        "mass": 5.927e24,
        "pos": np.array([0,0]),
        "vel": np.array([0,0]),
        "hist": []
    },
    "moon": {
        "mass": 7.342e22,
        "pos": np.array([0, 362600000]),
        "vel": np.array([-1022, 0]),
        "hist": []
    },
    "iss": {
        "mass": 419455,
        "pos": np.array([0, 409000 + 6370000]),
        "vel": np.array([-7660, 0]),
        "hist": []
    }
}

G = 6.67408e-11
speedup = 600
numberOfMiniSteps = 10

def runPhysics(dt):
    for name in bodies:
        if name == "earth": continue
        force = np.array([0,0])
        for name_ in bodies:
            if name == name_: continue
            r = bodies[name_]["pos"] - bodies[name]["pos"]
            force = force + G * bodies[name]["mass"] * bodies[name_]["mass"] / np.power(np.linalg.norm(r), 3) * r
        acc = force / bodies[name]["mass"]
        bodies[name]["vel"] = bodies[name]["vel"] + dt * acc
        bodies[name]["pos"] = bodies[name]["pos"] + dt * bodies[name]["vel"]

def toPlottingCoordinates(pos):
    scale = 50000000 / 300
    return (400 + int(pos[0] / scale), 300 - int(pos[1] / scale))

def drawDot(pos):
    pygame.draw.circle(DISPLAYSURF, [255,0,0], toPlottingCoordinates(pos), 8, 0)

def drawLines(hist):
    if len(hist) > 1:
        pygame.draw.lines(DISPLAYSURF, [255,0,0], 0, [ toPlottingCoordinates(pos) for pos in hist ])

while True:
    clock.tick(FPS)

    DISPLAYSURF.fill(WHITE)

    dt = float(clock.get_time()) / 1000
    for i in range(numberOfMiniSteps):
        runPhysics(speedup * dt / numberOfMiniSteps)

    for name, body in bodies.items():
        body["hist"].append(body["pos"])
        drawDot(body["pos"])
        drawLines(body["hist"])

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
