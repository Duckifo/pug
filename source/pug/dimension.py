from dataclasses import dataclass

import pygame
from pygame import Vector2

from pug.tree.node import Node
from pug.events import GETNODESIZE

@dataclass(frozen=False)
class Dim2():
  offset = Vector2()
  scale: Vector2 | None = None

  def absolute(self, area: Vector2) -> Vector2:
    if self.scale is None or self.scale.magnitude() == 0:
      return self.offset

    sl = area * self.scale
    return  + self.offset
