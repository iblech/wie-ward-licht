#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import pygame
import sys
from pygame.locals import *
from ringbuffer import *

FPS = 10

pygame.init()
DISPLAYSURF = pygame.display.set_mode((600, 600))
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GRAY  = (200, 200, 200)
clock = pygame.time.Clock()
pygame.display.set_caption("Gravitation")

bodies = {
    "earth": {
        "mass": 5.927e24,
        "pos": np.array([0.0, 0.0]),
        "vel": np.array([0.0, 0.0]),
    },
    "moon": {
        "mass": 7.342e22,
        "pos": np.array([0.0, 362600000]),
        "vel": np.array([-1022, 0.0]),
    },
    "iss": {
        "mass": 419455,
        "pos": np.array([0.0, 409000 + 6370000]),
        "vel": np.array([-7660.0, 0.0]),
    },
    "l1": {
        "mass": 100,
        "pos": np.array([0.0, 362600000 * (1 - np.power(7.342e22 / (3*5.927e24), 1/3))]),
        "vel": np.array([-1022 * (1 - np.power(7.342e22 / (3*5.927e24), 1/3)), 0.0]),
    },
    "l5": {
        "mass": 100,
        "pos": np.array([np.cos(np.pi / 100) * 362600000, np.sin(np.pi / 100) * 362600000]),
        "vel": 1022 * np.array([np.cos(np.pi * (1/100 + 1/2)), np.sin(np.pi * (1/100 + 1/2))]),
    }
}

G = 6.67408e-11
speedup = 86400
dt = 500

def calcAcceleration(name):
    force = np.array([0,0])
    for name_ in bodies:
        if name == name_: continue
        r = bodies[name_]["pos"] - bodies[name]["pos"]
        force = force + G * bodies[name]["mass"] * bodies[name_]["mass"] / np.power(np.linalg.norm(r), 3) * r
    return force / bodies[name]["mass"]

def runFirstPhysicsStep(dt):
    for name in bodies:
        if name == "earth": continue
        bodies[name]["vel"] = bodies[name]["vel"] + dt * calcAcceleration(name) / 2

def runPhysics(dt):
    for name in bodies:
        if name == "earth": continue
        bodies[name]["pos"] = bodies[name]["pos"] + dt * bodies[name]["vel"]
        acc = calcAcceleration(name)
        bodies[name]["vel"] = bodies[name]["vel"] + dt * acc

def toPlottingCoordinates(pos):
    scale = 700000000 / 300
    return (300 + int(pos[0] / scale), 300 - int(pos[1] / scale))

def drawDot(pos, color):
    pygame.draw.circle(DISPLAYSURF, color, toPlottingCoordinates(pos), 8, 0)

def drawLines(hist):
    if len(hist) > 1:
        pygame.draw.lines(DISPLAYSURF, [255,0,0], 0, [ toPlottingCoordinates(pos) for pos in hist ])

for name in bodies:
    bodies[name]["hist"] = Ringbuffer(20)

simulatedTime = 0
userTime      = 0

runFirstPhysicsStep(dt)

DISPLAYSURF.fill(WHITE)

while True:
    userTime = userTime + clock.tick(FPS) * speedup / 1000
    print userTime / speedup

    while simulatedTime < userTime:
        runPhysics(dt)
        simulatedTime = simulatedTime + dt

    for name, body in bodies.items():
#       body["hist"].push(body["pos"])
        drawDot(body["pos"], RED)
#       drawLines(body["hist"].list())
    pygame.display.update()
    for name, body in bodies.items():
        drawDot(body["pos"], GRAY)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
