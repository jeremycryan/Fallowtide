import math
import pygame

DEBUG = True

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

CAPTION = "Fallowtide"
FRAMERATE = 60

WHEAT = 0
FENNEL = 1
FELLWEED = 2
MULCH = 3
BLOOD = 4
GOAT = 5
CULTIST = 6

DOWN = 0
UP = 1
EITHER = 2

CARD_NAMES = {
    WHEAT: "Wheat",
    FENNEL: "Fennel",
    FELLWEED: "Hellweed",
    MULCH: "Mulch",
    BLOOD: "Blood",
    GOAT: "Goat",
    CULTIST: "Offering",
}

TILE_PRICES = {
    WHEAT: 100,
    FENNEL: 400,
    FELLWEED: 1200,
    MULCH: 0,
    BLOOD: 0,
    GOAT: 0,
    CULTIST: 0
}

CARD_WIDTH = 250
CARD_HEIGHT = 350
CARD_SPACING = 15

CARD_SHAPE_WIDTH = 70
CARD_SHAPE_SPACING = 7

HEALTHY = 0
USED = 1
BARREN = 2


WHEAT_SHAPES = {

}

CROP_DESCRIPTIONS = {
    FELLWEED: "Makes soil barren",
    MULCH: "Replenish soil",
    BLOOD: "All is forgiven",
    GOAT: "Life from death",
    CULTIST: "A willing sacrifice",
}

COMPOSTS_TO = {
    FELLWEED: MULCH,
    GOAT: BLOOD,
    WHEAT: MULCH,
    FENNEL: MULCH,
}

SMALL_SHAPES = [
    (((0, 0), (1, 0)), DOWN),
    (((0, 0), (1, 0)), UP),
    (((0, 0), (0, -1)), DOWN),
]

MEDIUM_SHAPES = [
    (((0, 0), (0, -1), (1, 0), (-1, 0)), DOWN), # triforce
    (((1, 0), (0, 0), (0, -1), (1, -1)), DOWN), # < pacman
    (((0, 0), (1, 0), (1, -1), (0, -1)), UP), # > pacman
    (((0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)), UP),
    (((0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0)), DOWN),
    (((0, 0), (1, 0), (1, 1), (2, 1), (3, 1)), DOWN),
    (((1, 0), (0, 0), (0, 1), (-1, 1), (-2, 1)), UP),
]

LARGE_SHAPES = [
    (((0, 0), (1, 0), (-1, 0), (2, 0), (0, 1), (-1, 1)), UP),
    (((0, 0), (-1, 0), (1, 0), (-2, 0), (0, 1), (1, 1)), UP),
    (((0, 0), (-1, 0), (1, 0), (-2, 0), (0, -1), (1, -1)), DOWN),
    (((0, 0), (1, 0), (-1, 0), (2, 0), (0, -1), (-1, -1)), DOWN),
    (((0, 0), (1, 0), (-1, 0), (1, 1), (0, 1), (-1, 1)), UP),
    (((0, 0), (1, 0), (-1, 0), (-1, -1), (1, -1), (0, 1)), UP),
    (((0, 0), (1, 0), (-1, 0), (-1, 1), (0, 1), (1, 1)), DOWN),
    (((0, 0), (1, 0), (-1, 0), (-1, 1), (0, 1), (1, 1), (2, 1)), DOWN),
    (((0, 0), (1, 0), (-1, 0), (-1, 1), (0, 1), (1, 1), (-2, 0)), DOWN),
    (((0, 0), (1, 0), (-1, 0), (-1, -1), (1, -1), (-2, -1), (2, -1), (0, 1)), UP),
    (((0, 0), (1, 0), (-1, 0), (-1, 1), (1, 1), (-2, 1), (2, 1), (0, -1)), DOWN),
]

BUY = 0
REMOVE = 1

CPS = 45 if not DEBUG else 4000
