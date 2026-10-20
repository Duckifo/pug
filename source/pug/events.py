import pygame

custom_index = 0
def new_event_index() -> int:
  global custom_index 
  event_index = pygame.USEREVENT + custom_index 
  custom_index += 1
  return event_index

HIT = new_event_index()
HITSCAN = new_event_index()
RENDER = new_event_index()
REQUESTSIZE = new_event_index()
