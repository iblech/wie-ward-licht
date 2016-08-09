#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import pygame
import sys
from pygame.locals import *

FPS = 10

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock  = pygame.time.Clock()
pygame.display.set_caption("Gravitation")

def rotationMatrix(phi):
    return np.array([[np.cos(phi), -np.sin(phi)], [np.sin(phi), np.cos(phi)]])

G      = 6.67408e-11
bodies = {
    "earth": {
        "mass":  5.927e24,
        "pos":   np.array([0.0, 0.0]),
        "vel":   np.array([0.0, 0.0]),
        "color": (0,0,200),
    },
    "moon": {
        "mass":  7.342e22,
        "pos":   np.array([0.0, 362600000]),
        "vel":   np.array([-1022, 0.0]),
        "color": (100,100,100),
    },
    "iss": {
        "mass":  419455,
        "pos":   np.array([0.0, 409000 + 6370000]),
        "vel":   np.array([-7660.0, 0.0]),
        "color": (255,0,0),
    },
    "rocket": {
        "mass":  100,
        "pos":   np.dot(rotationMatrix(-0.1), np.array([0.0, 409000 + 6370000])),
        "vel":   np.dot(rotationMatrix(-0.1), np.array([-7660.0, 0.0])),
        "color": (255,150,0),
    },
    "l5": {
        "mass":  0,
        "pos":   np.dot(rotationMatrix(-np.pi/3), np.array([0.0, 362600000])),
        "vel":   np.dot(rotationMatrix(-np.pi/3), np.array([-1022, 0.0])),
        "color": (0,0,0),
    },
    "trojan": {
        "mass":  0,
        "pos":   np.dot(rotationMatrix(-np.pi/3), np.array([0.0, 362600000])),
        "vel":   np.dot(rotationMatrix(-np.pi/3), np.array([-1022, 0.0])),
        "color": (150,255,0),
    },
}

def calcAcceleration(name):
    acc = np.array([0,0])
    for name_ in bodies:
        if name == name_ or bodies[name_]["mass"] == 0: continue
        r = bodies[name_]["pos"] - bodies[name]["pos"]
        acc = acc + G * bodies[name_]["mass"] / np.power(np.linalg.norm(r), 3) * r
    return acc

def runFirstPhysicsStep(dt):
    for name in bodies:
        if name == "earth": continue
        bodies[name]["vel"] = bodies[name]["vel"] + dt * calcAcceleration(name) / 2

def runPhysics(dt):
    for name in bodies:
        if name == "earth": continue
        bodies[name]["pos"] = bodies[name]["pos"] + dt * bodies[name]["vel"]
    acc = {}
    for name in bodies:
        acc[name] = calcAcceleration(name)
    for name in bodies:
        bodies[name]["vel"] = bodies[name]["vel"] + dt * acc[name]

def toPlottingCoordinates(pos):
    imagePos = np.dot(rotationMatrix(cameraAngle), pos - cameraOrigin)
    return (300 + int(imagePos[0] / cameraScale), 300 - int(imagePos[1] / cameraScale))

def fromPlottingCoordinates(imagePos):
    x, y = cameraScale * (imagePos[0] - 300.0), cameraScale * (300.0 - imagePos[1])
    return np.dot(rotationMatrix(-cameraAngle), np.array([x,y])) + cameraOrigin

def drawDot(pos, mass, color):
    radius = 3 if mass == 0 else int(6 + np.log(mass) / 5)
    pygame.draw.circle(screen, color, toPlottingCoordinates(pos), radius, 0)

simulatedTime = 0
userTime      = 0
speedup       = 60
dt            = 1

cameraType    = 0

runFirstPhysicsStep(dt)

screen.fill((255,255,255))

while True:
    userTime = userTime + clock.tick(FPS) * speedup / 1000
    print userTime

    while simulatedTime < userTime:
        runPhysics(dt)
        simulatedTime = simulatedTime + dt

    if cameraType == 0:
        cameraDescr  = u"In der Mitte die Rakete, links wäre die Erde (mitrotierendes Bezugssystem)"
        cameraScale  = 5000.0
        cameraAngle  = -np.arctan2(bodies["rocket"]["pos"][1], bodies["rocket"]["pos"][0])
        cameraOrigin = bodies["rocket"]["pos"]
    elif cameraType == 1:
        cameraDescr  = u"In der Mitte die Erde, außen die ISS sichtbar (ruhendes Bezugssystem)"
        cameraScale  = 60000.0
        cameraAngle  = 0
        cameraOrigin = np.array([0.0, 0.0])
    elif cameraType == 2:
        cameraDescr  = u"In der Mitte die Erde, außen der Mond sichtbar (ruhendes Bezugssystem)"
        cameraScale  = 2000000.0
        cameraAngle  = 0
        cameraOrigin = np.array([0.0, 0.0])
    elif cameraType == 3:
        cameraDescr  = u"In der Mitte L5 (mitrotierendes Bezugssystem)"
        cameraScale  = 5000.0
        cameraAngle  = -np.arctan2(bodies["l5"]["pos"][1], bodies["l5"]["pos"][0])
        cameraOrigin = bodies["l5"]["pos"]

    for name, body in bodies.items():
        drawDot(body["pos"], body["mass"], body["color"])
    pygame.draw.rect(screen, (255,255,255), (0,0, 600, 25))
    screen.blit(pygame.font.Font(None, 25).render(cameraDescr, 1, (10,10,10)), (0,0))
    pygame.display.update()
    for name, body in bodies.items():
        drawDot(body["pos"], body["mass"], (200,200,200))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = fromPlottingCoordinates(pygame.mouse.get_pos()) - cameraOrigin
            if event.button == 1:
                bodies["rocket"]["vel"] = bodies["rocket"]["vel"] + pos / 20000
            else:
                bodies["trojan"]["vel"] = bodies["trojan"]["vel"] + pos / 200000
        elif event.type == pygame.KEYUP and event.key == pygame.K_c:
            cameraType = (cameraType + 1) % 4
        elif event.type == pygame.KEYUP and event.key == pygame.K_UP:
            speedup = 2 * speedup
            dt      = 2 * dt
        elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            speedup = 0.5 * speedup
            dt      = 0.5 * dt
