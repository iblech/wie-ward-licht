#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np
import pygame
from pygame.locals import *
import sys

#####################################################################
# Hier die Zustandsvariablen initialisieren: Höhe und Geschwindigkeit
#####################################################################

# h = ...
# v = ...


#####################################################################
# Hier den Code schreiben, um die simulierte Zeit um dt Sekunden
# weiterlaufen zu lassen
#####################################################################
def runPhysics(dt):
    global h, v
    # h = ...
    # v = ...


#####################################################################
# Hier den Code schreiben, um die Rakete zu zeichnen
#####################################################################
def drawScene():
    pygame.draw.rect(screen, (255,0,0), (17, 230, 50, 100), 0)


#####################################################################
# Initialisierung der PyGame-Bibliothek
#####################################################################
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock  = pygame.time.Clock()
pygame.display.set_caption("Yeah, Marslandung")

speedup       = 10     # Zeitrafferfaktor
dt            = 0.1    # Zeitschrittgröße der Physik-Engine
userTime      = 0      # Realzeit seit Programmbeginn (in Sekunden)
simulatedTime = 0      # Simulierte Zeit seit Programmbeginn (in Sekunden)
FPS           = 10     # Frames pro Sekunde


#####################################################################
# Die Hauptschleife des Programms (hier muss zunächst nichts gemacht
# werden)
#####################################################################
while True:
    userTime = userTime + clock.tick(FPS) * speedup / 1000
    print userTime

    # Physik-Engine so oft aufrufen, bis die simulierte Zeit die Realzeit
    # eingeholt hat
    while simulatedTime < userTime:
        runPhysics(dt)
        simulatedTime = simulatedTime + dt

    screen.fill((255,255,255))
    drawScene()
    pygame.display.update()

    # Verarbeitung von ausgelösten Events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Verarbeitung von gedrückten Tasten
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_RIGHT]:
        print("Rechtstaste gedrückt!")
    elif pressed[pygame.K_LEFT]:
        print("Linkstaste gedrückt!")
