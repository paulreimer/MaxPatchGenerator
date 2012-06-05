"""
Copyright Paul Reimer, 2012

This work is licensed under the Creative Commons Attribution-NonCommercial 3.0 Unported License.
To view a copy of this license, visit
http://creativecommons.org/licenses/by-nc/3.0/
or send a letter to
Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.
"""

import json
from copy import copy, deepcopy

class Point(object):
  def __init__(self, *args):
    self.x = args[0]
    self.y = args[1]

  def translate(self, offset):
    self.x += offset.x
    self.y += offset.y

  def translated(self, offset):
    c = copy(self)
    c.x += offset.x
    c.y += offset.y
    return c

class MaxPatch(object):
  def __init__(self):
    self.patch = json.loads("""{
      "patcher":   {
        "fileversion": 1,
        "appversion":    {
          "major": 5,
          "minor": 1,
          "revision": 9
        },
        "rect": [ 126.0, 226.0, 640.0, 480.0 ],
        "bglocked": 0,
        "defrect": [ 126.0, 226.0, 640.0, 480.0 ],
        "openrect": [ 0.0, 0.0, 0.0, 0.0 ],
        "openinpresentation": 0,
        "default_fontsize": 12.0,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 0,
        "gridsize": [ 15.0, 15.0 ],
        "gridsnaponopen": 0,
        "toolbarvisible": 1,
        "boxanimatetime": 200,
        "imprint": 0,
        "enablehscroll": 1,
        "enablevscroll": 1,
        "devicewidth": 0.0,
        "boxes": [],
        "lines": []
      }
    }""")

    self.next_id = 0

  def new_id(self):
    self.next_id += 1
    return 'obj-{0}'.format(self.next_id)

  def add_box(self, maxclass='newobj', rect=[0, 0, 0, 0], numinlets=1, numoutlets=1, args={}):
    box = {
      'maxclass': maxclass,
      'outlettype': [ '' ],
      'patching_rect': rect,
      'id': self.new_id(),
      'numinlets': numinlets,
      'numoutlets': numinlets
      }
    box.update(args)

    self.patch['patcher']['boxes'].append({'box': box})
    return box

  def add_text_box(self, maxclass='newobj', rect=[0, 0, 0, 0], numinlets=1, numoutlets=1, args={}):
    text_box = {
      'fontname': 'Arial',
      'fontsize': 12.0,
      }
    text_box.update(args)

    return self.add_box(maxclass, rect, numinlets, numoutlets, text_box)

  def add_slider(self, rect=[0, 0, 0, 0], args={}):
    return self.add_box('slider', rect, args=args)

  def add_number(self, rect=[0, 0, 0, 0], datatype='int'):
    maxclass = 'number' if (datatype is 'int') else 'flonum'
    return self.add_text_box(maxclass, rect, 1, 2, {
      'outlettype': [ datatype, 'bang' ],
      })

  def add_toggle(self, rect=[0, 0, 0, 0], typetags=''):
    return self.add_box('toggle', rect=rect, args={
      'outlettype' : [ 'int' ]
      })

  def add_prepend(self, rect=[0, 0, 0, 0], addr='/'):
    return self.add_text_box(rect=rect, args={
      'text': 'prepend {0}'.format(addr),
      })

  def add_pack(self, rect=[0, 0, 0, 0], typetags=''):
    return self.add_text_box(rect=rect, numinlets=len(typetags), numoutlets=1, args={
      'text': 'pack ' + ' '.join(typetags),
      })

  def add_line(self, box1, box2, box1_outlet=0, box2_inlet=0):
    line = {'patchline': {
      'source' : [ box1['id'], box1_outlet ],
      'destination' : [ box2['id'], box2_inlet ],
      'hidden' : 0,
      'midpoints' : [ ]
      }}

    self.patch['patcher']['lines'].append(line)
    return line

