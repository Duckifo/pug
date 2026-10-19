import pygame

from pug.events import GETNODESIZE
from pug.tree.node import Node, on


'''
Root node is only used on the root of the DOM manager. It
implements basic edge cases for the event system. 
'''
class RootNode(Node):
  @on(GETNODESIZE, legate=False)
  def __get_node_size(self, e):
    ''' The root node needs to return the absolute size of the
    display, otherwise dim2 has nothing to reference. '''
    return pygame.Vector2(pygame.display.get_window_size())
