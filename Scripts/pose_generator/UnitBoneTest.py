# Test single bone movement

import bpy
from mathutils import Vector, Matrix

# 获取骨骼对象
armature = bpy.data.objects['rig']
bpy.context.view_layer.objects.active = armature

hand_l = armature.pose.bones['c_hand_ik.l']
hand_r = armature.pose.bones['c_hand_ik.r']
foot_l = armature.pose.bones['c_foot_ik.l']
foot_r = armature.pose.bones['c_foot_ik.r']
hip = armature.pose.bones['c_root_master.x']

# 设置帧速率
frame_rate = 24