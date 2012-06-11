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
from maxpatch import MaxPatch, Point
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

pos             = Point(10.0, 10.0)
padding         = 10.0
standard_height = 20.0

osc_size        = Point(113.0, standard_height)
udpsend_size    = Point(150.0, standard_height)
trigger_size    = Point(70.0,  standard_height)
loadbang_size   = Point(70.0,  standard_height)
preset_size     = Point(200.0, 52.0)

slider_size     = Point(140.0, standard_height)
toggle_size     = Point(20.0,  standard_height)
number_size     = Point(50.0,  standard_height)
pack_size       = Point(100.0, standard_height)
prepend_size    = Point(353.0, standard_height)
comment_size    = Point(180.0, standard_height)
defaults_size   = Point(60.0,  standard_height)

_offset         = pos.x

prepend_offset  = _offset
pack_offset     = _offset
_offset         += prepend_size.x + padding

number_offset   = _offset
_offset         += number_size.x + padding

slider_offset   = _offset
_offset         += slider_size.x + padding

defaults_offset = _offset
_offset         += defaults_size.x + padding

comment_offset  = _offset
_offset         += comment_size.x + padding

preset_offset   = number_offset
loadbang_offset = defaults_offset

patch = MaxPatch()

x = pos.x

trigger_rect = [x, pos.y, trigger_size.x, trigger_size.y]
trigger = patch.add_newobj('trigger b s', trigger_rect, numinlets=1, numoutlets=2, args={
  'outlettype' : [ 'bang', 'string' ],
  })
x += trigger_size.x + padding

osc_rect = [x, pos.y, osc_size.x, osc_size.y]
osc_obj = patch.add_newobj('OpenSoundControl', osc_rect, args={
  'outlettype' : [ '', '', 'OSCTimeTag' ],
  })
x += osc_size.x + padding

udpsend_rect = [x, pos.y, udpsend_size.x, udpsend_size.y]
udpsend = patch.add_newobj('udpsend 127.0.0.1 12345', udpsend_rect, numinlets=1, numoutlets=0)
x += udpsend_size.x + padding

loadbang_rect = [loadbang_offset, pos.y, loadbang_size.x, loadbang_size.y]
loadbang = patch.add_newobj('loadbang', loadbang_rect, numinlets=1, numoutlets=0)

preset_rect = [preset_offset, pos.y, preset_size.x, preset_size.y]
preset = patch.add_preset(preset_rect)

patch.add_line(trigger, osc_obj, 0, 0)
patch.add_line(trigger, osc_obj, 1, 0)

patch.add_line(osc_obj, udpsend)

pos.y += osc_size.y + padding

def make_osc_message(patch, osc_obj, addr, typetags, comments=[], defaults=[], bounds_list=[], pos=Point(0, 0), padding=10.0):
  pos             = copy(pos)
  _starty = pos.y

  prepend = patch.add_prepend([prepend_offset, pos.y, prepend_size.x, prepend_size.y], addr)
  patch.add_line(prepend, osc_obj, hidden=True)
  pos.y += prepend_size.y + padding

  if len(typetags) > 0:
    pack_tags = map(lambda t: pack_typetags[t], typetags)
    pack = patch.add_pack([pack_offset, pos.y, pack_size.x, pack_size.y], pack_tags)
    patch.add_line(pack, prepend)

  pos.y = _starty

  for idx,arg in enumerate(typetags):
    if idx < len(comments):
      patch.add_comment(comments[idx], [comment_offset, pos.y, comment_size.x, comment_size.y])

    bounds = (0.0, 1.0)
    adjust = None
    if idx < len(bounds_list) and bounds_list[idx] is not None:
      bounds = bounds_list[idx]

    defaults_msg = None
    if idx < len(defaults) and defaults[idx] is not None:
      default = defaults[idx]
      if default == True: default = 1;
      if default == False: default = 0;
      defaults_msg = patch.add_message(default, [defaults_offset, pos.y, defaults_size.x, defaults_size.y])

      if bounds[0] is not 0.0:
        args = {}
        if arg is 'f':
          args['outlettype'] = [ 'float' ]
        adjust = patch.add_newobj('- '+str(bounds[0]), [defaults_offset, pos.y, 0.0, 0.0], numinlets=2, args=args)
        patch.add_line(defaults_msg, adjust)

    if arg in ['f', 'i']:
      if arg is 'i':
        slider = patch.add_slider([slider_offset, pos.y, slider_size.x, slider_size.y], bounds)
        number = patch.add_number([number_offset, pos.y, number_size.x, number_size.y])

      elif arg is 'f':
        slider = patch.add_slider([slider_offset, pos.y, slider_size.x, slider_size.y], bounds, {
          'floatoutput': 1,
          'size': 1.0,
          })
        number = patch.add_number([number_offset, pos.y, number_size.x, number_size.y], 'float')

      patch.add_line(slider, number)
      patch.add_line(number, pack, 0, idx)

      if adjust is not None:
        patch.add_line(adjust, slider)
      elif defaults_msg is not None:
        patch.add_line(defaults_msg, slider)

    elif arg in ['b']:
      toggle = patch.add_toggle([slider_offset, pos.y, toggle_size.x, toggle_size.y])

      patch.add_line(toggle, pack, 0, idx)

      if defaults_msg is not None:
        patch.add_line(defaults_msg, toggle)

    elif arg in ['s']:
      pass

    pos.y += standard_height + padding

  extrapadding = 2 - len(typetags)
  if extrapadding > 0:
    pos.y += extrapadding*(standard_height + padding)

  pos.y += 2*padding

  return pos

def walk_protobuf_descriptor(patch, osc_obj, desc, path_segments, pos, padding=10.0):
  newpos = pos

  if desc.name in ignore_types:
    pass

  elif desc.name in leaf_types:
    addr = '/'.join(path_segments)
    typetags = map(lambda f: osc_typetags[f.type], desc.fields)
    comments = map(lambda i: desc.fields[i].name, range(0, len(desc.fields)))
    defaults = map(lambda f: None if not f.has_default_value else f.default_value, desc.fields)
    paths = map(lambda f: ('/'.join(path_segments)+':'+f.name), desc.fields)
    bounds_list = map(lambda p: bounds_for_full_name.get(p, None), paths)

    newpos = make_osc_message(patch, osc_obj, addr, typetags, comments, defaults, bounds_list, pos=pos, padding=padding)

  else:
    for field in desc.fields:
      if hasattr(field, 'message_type') and field.message_type:
        path_segments.append(field.name)
        newpos = walk_protobuf_descriptor(patch, osc_obj, field.message_type, path_segments, newpos)

      else:
        addr = '/'.join(path_segments+[field.name])
        typetags = osc_typetags[field.type]
        comments = [field.name]
        defaults = [] if not field.has_default_value else [field.default_value]
        path = '/'.join(path_segments+[field.name])
        bounds_list = [bounds_for_full_name.get(path, None)]

        newpos = make_osc_message(patch, osc_obj, addr, typetags, comments, defaults, bounds_list, pos=newpos, padding=padding)

  path_segments.pop()
  return newpos

walk_protobuf_descriptor(patch, trigger, pb.DESCRIPTOR, osc_root_path_segments, pos)

print json.dumps(patch.patch, indent=4)

