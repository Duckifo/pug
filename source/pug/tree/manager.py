from dataclasses import dataclass
from typing import Dict, Literal

import pygame

from node import Node, UiNode
from pygame import Vector2

from source.pug.nodes.core import RootNode

class Manager:
  def __init__(self):
    self.root = RootNode()
    self.focused = self.root

  def route_event(self, event):
    pass
