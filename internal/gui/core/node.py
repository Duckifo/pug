from types import MappingProxyType
from typing import Any, Callable, ClassVar, Self

import pygame


def on(*events: int, legate = True):
  def decorator(func: Callable[[Any, pygame.event.Event], None]):
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
        Callable[[Self, pygame.event.Event], None]
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

  def __init__(self):

