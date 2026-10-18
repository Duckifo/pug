from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, ClassVar, FrozenSet, List, final

from pygame import Vector2, Vector3

# A decorator that defines a class method to be a socket, of name `socket`.
def socket(func: Callable):
  setattr(func, "_issocket", True)
  return func


''' 
An element is non-visual component that implements simple socket functionality. 
'''
class Element(ABC):
  # A list for all defined sockets of the class.
  sockets: ClassVar[FrozenSet[str]]

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)

    # Define which methods are considered to be sockets.
    own = frozenset(name for name, attr in vars(cls).items() if getattr(attr, "_issocket", False))
    inherited = frozenset().union(*(b.sockets for b in cls.__bases__ if hasattr(b, "sockets")))
    cls.sockets = inherited | own

  # Checks if the current class implements socket with
  # passed name.
  @classmethod
  def implements(cls, socket: str):
    return socket in cls.sockets

  def __init__(self, 
    id: str | None = None,
    parent: Element | None = None,
    zindex: int = 0
  ):
    self.id = id
    self.parent = parent
    self.zindex = zindex
    self._children: List[Element] = []


  @final
  # Appends a child to this element.
  def append_child(self, child: Element):
    if child.parent is not None: child.parent.remove_child(child)
    child.parent = self
    self._children.append(child)
    self._children.sort(key=lambda e: e.zindex) # sort the list

  @final
  # Removes a child from this element.
  def remove_child(self, child: Element): 
    self._children.remove(child)

  @final
  # Get a copy of the children list.
  def get_children(self) -> List[Element]:
    return self._children.copy()

  @final
  # Gets one or more children from the element via an
  # string identifier. Children with the highest z-index
  # comes last in the returned list.
  def get_children_of_id(self, id: str) -> List[Element]:
    return [child for child in self._children if child.id == id]

  @final
  # Emits arguments to passed socket. If socked does not exists raises a
  # NotImplemented error. Bubble means that the signal should go to the
  # closest parenting element that implements said socket.
  def emit(self, socket: str, *args, bubble=False, **kwargs):
    if not self.implements(socket):
      if not bubble: raise NotImplementedError("Method is not implemented.")
      if self.parent is not None:
        self.parent.emit(socket, *args, bubble=True, **kwargs)
      return

    getattr(self,socket)(**kwargs)
  
  @final
  # Broadcast a socket to this element and all it's children. The element with
  # the highest z-index gets the signal last (if function not reversed).
  def broadcast(self, socket: str, *args, reverse=False, **kwargs):
    def emit_self():
      if not self.implements(socket): return
      try: self.emit(socket, *args, bubble=False, **kwargs)
      except Exception as e: 
        print(f"Failed to execute signal {socket} for object {self}.")
    
    if not reverse: emit_self()
    children = reversed(self._children) if reverse else self._children
    for child in children:
      child.broadcast(socket, reverse=reverse, **kwargs) 
    if reverse: emit_self()

  def focus_from_point(self, point) -> Element | None:
    for child in reversed(self._children):
      hit = child.focus_from_point(point)
      if hit is not None:
        return hit
    return self



'''
An UiElement is derived from the non-visual Element, but here it gets a
position, size and a bunch of sockets that an UiManager can use to manage these
components.
'''
class UiElement(Element):
  def __init__(self,
    id: str | None = None,
    parent: Element | None = None,
    zindex: int = 0,

    position = Vector2(0,0),
    size = Vector2(0,0)
  ):
    super().__init__(
      id = id, parent = parent, zindex = zindex
    )

    self.position = Vector2(0,0)
    self.size = Vector2(0,0)


  @final
  def point_overlap_area(self, point: Vector2):
    return (
      self.position.x <= point.x and 
      self.position.x + self.size.x >= point.x and
      self.position.y <= point.y and
      self.position.y + self.size.y >= point.y
    )

  def focus_from_point(self, point: Vector2):
    for child in reversed(self._children):
      hit = child.focus_from_point(point)
      if hit is not None:
        return hit
    return self if self.point_overlap_area(point) else None


  # SOCKETS:

  def update(self):
    ''' 
    An event socket that fires every time the element has an update. It fires
    along a bunch of other sockets, it's more of a collection then a socket of
    it's own.
    '''

  def on_clicked(self, pos: Vector2):
    '''
    An event socket that fires every time the user clicks on the element. For
    the click to register to the element, this element has to be focused by the
    manager.
    '''

  def on_mouse_moved(self, pos: Vector2):
    '''
    An event socket that fires every time the user moves the mouse over the
    element. Requires manager focus.
    '''

  def render(self):
    '''
    When this socket is fired, the element should be rendered to the screen.
    Firing could be managed by parent element.
    '''

