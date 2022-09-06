import sys
import os
import pygame as pg

pg.init()

BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
