
from pygame.event import Event

from source.pug.events import RENDER, REQUESTSIZE
from source.pug.tree.node import UiNode, on


class Frame(UiNode):
  @on(RENDER)
  def render(self, event):
    size = self.size.absolute()
    pos = self.position.absolute()
