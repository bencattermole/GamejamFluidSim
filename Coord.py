import math
import pygame
import time
import random


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)


def generate_empty(Screen_Size):
    temp = {}
    for i in range(Screen_Size+1):
        for j in range(Screen_Size+1):
            temp[Coord(i, j)] = 0.0

    return temp
