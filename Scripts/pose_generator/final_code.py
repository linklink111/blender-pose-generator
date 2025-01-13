import bpy
from mathutils import Vector, Matrix

# 确保代码基于世界坐标方向进行增量操作
import bpy
# 获取骨骼对象
armature = bpy.data.objects['rig']  # 替换为你的骨骼名称
bpy.context.view_layer.objects.active = armature
left_foot = armature.pose.bones['c_foot_ik.l']
right_foot = armature.pose.bones['c_foot_ik.r']
hip = armature.pose.bones['c_root_master.x']

direction_text = "前方是+y，后方是-y，左边是-x，右边是+x，上方是+z，下方是-z。"

# 以下是一个简单的站立姿势

# 0.5s: 人物面向+y方向，向右迈出一步
frame_0_5 = 0.5 * frame_rate
right_foot.location += (armature.matrix_world @ (right_foot.parent.matrix if right_foot.parent else Matrix())).inverted() @ Vector(+Vector((1, 0, 0)) * 0.3)  # 向右迈出
right_foot.keyframe_insert(data_path="location", frame=frame_0_5)

# 1s: 人物向左转身，同时向后退一步
frame_1 = 1 * frame_rate
hip.rotation_euler.y -= 90  # 向左转身
hip.location += (armature.matrix_world @ (hip.parent.matrix if hip.parent else Matrix())).inverted() @ Vector(+Vector((0, 1, 0)) * 0.2)  # 向后退一步
hip.keyframe_insert(data_path="rotation_euler", frame=frame_1)
hip.keyframe_insert(data_path="location", frame=frame_1)

# 1.5s: 人物向上抬头，同时左脚向左跨出
frame_1_5 = 1.5 * frame_rate
head.rotation_euler.x += 45  # 抬头
left_foot.location -= (armature.matrix_world @ (left_foot.parent.matrix if left_foot.parent else Matrix())).inverted() @ Vector(-Vector((1, 0, 0)) * 0.2)  # 向左跨出
head.keyframe_insert(data_path="rotation_euler", frame=frame_1_5)
left_foot.keyframe_insert(data_path="location", frame=frame_1_5)