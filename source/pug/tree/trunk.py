from dataclasses import dataclass
from typing import Dict, Literal

from pug import events
from pug.nodes.core import RootNode

import pygame
from pygame.event import Event
from pygame import Vector2


class Trunk(RootNode):
  def __init__(self):
    super().__init__()
    self.focused = self

  def route_event(self, event: Event):
    match event.type:
      case pygame.MOUSEMOTION:
        pass
      case events.RENDER:
        self.focused.broadcast(event)
      case _:
        self.focused.emit(event, bubble=True)
