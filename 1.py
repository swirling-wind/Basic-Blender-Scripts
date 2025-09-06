import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *

cube = byp.context.scene.objects["Cube"]
#! Traceback (most recent call last):
#!   File "<blender_console>", line 1, in <module>
#! NameError: name 'byp' is not defined
#! 
cube = bpy.context.scene.objects["Cube"]
import bmesh
bm = bmesh.from_edit_mesh(cube.data)
len(bm.verts)
#~ 8
#~ 
v = bm.verts[3]
v.index
#~ 3
#~ 
v
#~ <BMVert(0x00000264F4D36B78), index=3>
#~ 
v.co
#~ Vector((1.0, -1.0, -1.0))
#~ 
v.co
#~ Vector((1.0, -1.0, -1.0))
#~ 
v.co[1] += 1
bmesh.update_edit_mesh(cube.data)