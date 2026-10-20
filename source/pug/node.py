from __future__ import annotations
from types import MappingProxyType
from typing import Any, Callable, ClassVar, List, Self, _get_type_hints_obj_allowed_types, final

from pygame.event import Event

from pug.dimension import Dim2
from pug.events import HIT, HITSCAN, REQUESTSIZE

import pygame
from pygame import Vector2

def on(*events: int, legate = True):
  def decorator(func: Callable[[Any, pygame.event.Event], Any]):
    setattr(func, "__pygameevents__", events)
    setattr(func, "__legateevents__", legate)
    return func
  return decorator

'''
A Node is a non-visual element that can be added to a
manager. It controlled via events, assigned by `on()`
decorator.
'''
class Node:
  # A read only dictionary that routes methods.
  class_events: ClassVar[
      MappingProxyType[
        int,
        Callable[[Self, pygame.event.Event], Any]
      ]
  ]

  def __init_subclass__(cls) -> None:
    super().__init_subclass__()
    
    # Get the base class events.
    class_events = (
        getattr(cls.__base__,"class_events").copy() 
        if cls.__base__ is not None 
        and hasattr(cls.__base__, "class_events")
        else {}
    )

    class_events = {
      k: v for k, v in class_events.items() 
      if getattr(v, "__legateevents__") == True
    }

    # Enter the new ones.
    for name, attr in vars(cls).items():
      events = getattr(attr, "__pygameevents__", None) 
      if events is None: continue
      for event in events:
        class_events[event] = attr

    # Assign to this classes events.
    cls.class_events = MappingProxyType(class_events)

  @classmethod
  # Checks if the current class implements passed event.
  def implements(cls, event: int) -> bool:
    return event in cls.class_events

  
  '''
  Node object start.
  '''

  def __init__(self, 
    id: str | None = None,
    parent: Node | None = None,
    zindex: int = 0
  ):
    self.id = id
    self.parent = parent
    self.zindex = zindex
    self._children: List[Node] = []


  @final
  # Appends a child to this node.
  def append_child(self, child: Node):
    if child.parent is not None: child.parent.remove_child(child)
    child.parent = self
    self._children.append(child)
    self._children.sort(key=lambda e: e.zindex) # sort the list

  @final
  # Removes a child from this node.
  def remove_child(self, child: Node): 
    self._children.remove(child)

  @final
  # Get a copy of the children list.
  def get_children(self) -> List[Node]:
    return self._children.copy()

  @final
  # Gets one or more children from the node via an
  # string identifier. Children with the highest z-index
  # comes last in the returned list.
  def get_children_of_id(self, id: str) -> List[Node]:
    return [child for child in self._children if child.id == id]

  @final
  # Emits arguments to passed event. If event does not exists raises a
  # NotImplemented error. Bubble means that the signal should go to the
  # closest parenting node that implements said event. If
  # event raises exception, forwards exception.
  def emit(self, event: int, *args, bubble=False, **kwargs) -> Any:
    if not self.implements(event):
      if not bubble: raise NotImplementedError("Method is not implemented.")
      if self.parent is not None:
        self.parent.emit(event, *args, bubble=True, **kwargs)
      return

    try: 
      return self.class_events[event](self, *args, **kwargs)
    except Exception as e:
        raise e
  
  @final
  # Broadcast a event to this node and all it's children.
  # The node with the highest z-index gets the signal last
  # (if function not reversed).
  def broadcast(self, event: int, *args, reverse=False, **kwargs):
    def emit_self():
      if not self.implements(event): return
      try: self.emit(event, *args, bubble=False, **kwargs)
      except Exception as e: 
        print(f"Failed to execute signal {event} for object {self}.")
    
    if not reverse: emit_self()
    children = reversed(self._children) if reverse else self._children
    for child in children:
      child.broadcast(event, reverse=reverse, **kwargs) 
    if reverse: emit_self()


'''
UiNode derives from Node, but implements rendering events
and hit management.
'''
class UiNode(Node):
    def __init__(self,
        id: str | None = None,
        parent: Node | None = None,
        zindex: int = 0,
        size = Dim2(),
        pos  = Dim2()
    ):
        super().__init__(id, parent, zindex)

        self.size = size
        self.position = pos

    @on(HITSCAN)
    def hitscan(self, event) -> Node:
      point: Vector2 = event.point_v2
      if point is None: return self
      for child in self._children:
        return child.emit(event,bubble=False)

    @on(HIT)
    def hit(self, event) -> bool:
      point: Vector2 = event.point_v2
      if point is None: return False
      return (
        self.emit(Event(REQUESTSIZE))
      )


    @on(REQUESTSIZE)
    def get_node_size(self, event):
      if self.parent is None: return self.size.offset
      return self.size.absolute(
          self.parent.emit(REQUESTSIZE,bubble=True)
      )
