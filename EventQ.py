# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 22:26:35 2017

@author: danz
"""

import heapq

class Event:
    def __init__(self, ts, eType, eData):
		# when does the event happen?
        self.ts = ts
		# event type
        self.eType = eType
		# event meta data
        self.eData = eData
        
    def __lt__(self, other):
        return self.ts < other.ts
        
class EventQ:
    def __init__(self):
        self.h = []
        
    def __len__(self):
        return len(self.h)
    
    def push(self, event):
        heapq.heappush(self.h, event)
        
    def pop(self):
        return heapq.heappop(self.h)
