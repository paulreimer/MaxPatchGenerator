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
from maxpat import *
from custom import *
from google.protobuf.descriptor import FieldDescriptor

osc_typetags = {
  FieldDescriptor.TYPE_STRING   : 's',
  FieldDescriptor.TYPE_BOOL     : 'b',
  FieldDescriptor.TYPE_BYTES    : None,
  FieldDescriptor.TYPE_DOUBLE   : 'f',
  FieldDescriptor.TYPE_ENUM     : None,
  FieldDescriptor.TYPE_FIXED32  : 'i',
  FieldDescriptor.TYPE_FIXED64  : 'i',
  FieldDescriptor.TYPE_FLOAT    : 'f',
  FieldDescriptor.TYPE_GROUP    : None,
  FieldDescriptor.TYPE_INT32    : 'i',
  FieldDescriptor.TYPE_INT64    : 'i',
  FieldDescriptor.TYPE_MESSAGE  : None,
  FieldDescriptor.TYPE_SFIXED32 : 'i',
  FieldDescriptor.TYPE_SFIXED64 : 'i',
  FieldDescriptor.TYPE_SINT32   : 'i',
  FieldDescriptor.TYPE_SINT64   : 'i',
  FieldDescriptor.TYPE_UINT32   : 'i',
  FieldDescriptor.TYPE_UINT64   : 'i',
  }

pack_typetags = {
  's': 's',
  'i': '0',
  'b': '0', # cast to int {0,1}
  'f': '0.',
  }

def make_osc_message(patch, addr, typetags, ranges=[], pos=Point(0, 0)):
  pos             = copy(pos)
  padding         = 10.0

  slider_size     = Point(140.0, 20.0)
  toggle_size     = Point(20.0, 20.0)
  number_size     = Point(50.0, 20.0)
  pack_size       = Point(100.0, 20.0)
  prepend_size    = Point(330.0, 20.0)

  _offset = pos.x
  _starty = pos.y
  prepend_offset = _offset
  pack_offset = _offset
  _offset += prepend_size.x + padding

  number_offset = _offset
  _offset += number_size.x + padding

  slider_offset = _offset
  _offset += slider_size.x + padding

  prepend = patch.add_prepend([prepend_offset, pos.y, prepend_size.x, prepend_size.y], addr)
  pos.y += prepend_size.y + padding

  if len(typetags) > 0:
    pack_tags = map(lambda t: pack_typetags[t], typetags)
    pack = patch.add_pack([pack_offset, pos.y, pack_size.x, pack_size.y], pack_tags)
    patch.add_line(pack, prepend)

  pos.y = _starty

  for idx,arg in enumerate(typetags):
    if arg in ['f', 'i']:
      if arg is 'i':
        slider = patch.add_slider([slider_offset, pos.y, slider_size.x, slider_size.y])
        number = patch.add_number([number_offset, pos.y, number_size.x, number_size.y])
      elif arg is 'f':
        slider = patch.add_slider([slider_offset, pos.y, slider_size.x, slider_size.y], {
          'floatoutput': 1,
          'size': 1.0,
          })
        number = patch.add_number([number_offset, pos.y, number_size.x, number_size.y], 'float')

      patch.add_line(slider, number)
      patch.add_line(number, pack, 0, idx)

    elif arg in ['b']:
      toggle = patch.add_toggle([slider_offset, pos.y, toggle_size.x, toggle_size.y])

      patch.add_line(toggle, pack, 0, idx)

    elif arg in ['s']:
      pass

    pos.y += slider_size.y + padding

  if len(typetags) is 1:
    pos.y += slider_size.y + padding

  pos.y += 2*padding

  return pos

def walk_protobuf_descriptor(patch, desc, path, pos):
  newpos = pos

  if desc.name in ignore_types:
    path.pop()
    return newpos

  if desc.name in composite_types:
    addr = '/'.join(path)

    typetags = map(lambda f: osc_typetags[f.type], desc.fields)
    newpos = make_osc_message(patch, addr, typetags, pos=pos)

  else:
    for field in desc.fields:
      if hasattr(field, 'message_type') and field.message_type:
        path.append(field.name)
        newpos = walk_protobuf_descriptor(patch, field.message_type, path, newpos)

      else:
        typetag = osc_typetags[field.type]
        addr = '/'.join(path+[field.name])
        newpos = make_osc_message(patch, addr, typetag, pos=newpos)

  path.pop()
  return newpos

startpos = Point(10.0, 10.0)

patch = MaxPatch()
walk_protobuf_descriptor(patch, pb.DESCRIPTOR, osc_root_path, startpos)

print json.dumps(patch.patch, indent=4)

