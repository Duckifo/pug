from dataclasses import dataclass
from typing import Dict, Literal

import pygame

from element import Element, UiElement
from pygame import Vector2

@dataclass(frozen=True)
class Route:
  socket: str
  bubble: bool
  target: Literal["hit", "focused", "captured"]


class Manager:
  def __init__(self):
    self.root = Element()
    self.focused = self.root

  def route_event(self, event):
    route = ROUTES.get(event.type)
    if route is None:
      return

    kwargs = route.args(event)
    if route.target == "all":
      self.root.broadcast(route.socket, **kwargs)
      return

    target = {
      "hit": lambda: self.hit_test(Vector2(event.pos)),
      "focused": lambda: self.focused,
      "captured": lambda: self.captured or self.hit_test(Vector2(event.pos)),
    }[route.target]()

    if target is not None:
      target.emit(route.socket, inheritance=route.bubble, **kwargs)
    
  def focus_from_point(self, point: Vector2):
    self.focused = self.root.focus_from_point(point) or self.root
