import bpy
from mathutils import Vector, Matrix

# 获取骨骼对象
armature = bpy.data.objects['rig']
bpy.context.view_layer.objects.active = armature

hand_l = armature.pose.bones['c_hand_ik.l']
hand_r = armature.pose.bones['c_hand_ik.r']
foot_l = armature.pose.bones['c_foot_ik.l']

# 设置帧速率
frame_rate = 24

# 初始站立姿势
frame_start = 0 * frame_rate
hand_l.location = (0.0, -0.5, 0.0)
hand_r.location = (0.0, 0.5, 0.0)
foot_l.location = (0.0, 0.0, 0.0)
foot_r.location = (0.0, 0.0, 0.0)

hand_l.keyframe_insert(data_path="location", frame=frame_start)
hand_r.keyframe_insert(data_path="location", frame=frame_start)
foot_l.keyframe_insert(data_path="location", frame=frame_start)
foot_r.keyframe_insert(data_path="location", frame=frame_start)

# 0.5s: 左脚向前迈出一步
frame_0_5 = 0.5 * frame_rate
# 对于任何骨骼请都严格按照这个方式来写，不要单独计算world matrix，否则会出错
foot_l.location += (armature.matrix_world @ (foot_l.parent.matrix if foot_l.parent else Matrix())).inverted() @ Vector((0, 0.2, 0))
hip.rotation_euler.y += 0.1
foot_l.keyframe_insert(data_path="location", frame=frame_0_5)
hip.keyframe_insert(data_path="rotation_euler", frame=frame_0_5)

# 1.0s: 左臂弯曲抬起
frame_1 = 1.0 * frame_rate
hand_l.location += (armature.matrix_world @ (hand_l.parent.matrix if hand_l.parent else Matrix())).inverted() @ Vector((0, -0.2, 0.8))
hand_l.rotation_euler.x += 1.0
hand_l.keyframe_insert(data_path="location", frame=frame_1)
hand_l.keyframe_insert(data_path="rotation_euler", frame=frame_1)

# 1.5s: 左臂向前甩动
frame_1_5 = 1.5 * frame_rate
hand_l.location += (armature.matrix_world @ (hand_l.parent.matrix if hand_l.parent else Matrix())).inverted() @ Vector((0, -0.5, 0))
hand_l.rotation_euler.x += 0.5
hand_l.keyframe_insert(data_path="location", frame=frame_1_5)
hand_l.keyframe_insert(data_path="rotation_euler", frame=frame_1_5)

# 2.0s: 左臂继续向前伸展
frame_2 = 2.0 * frame_rate
hand_l.location += (armature.matrix_world @ (hand_l.parent.matrix if hand_l.parent else Matrix())).inverted() @ Vector((0, -0.2, 0))
hand_l.keyframe_insert(data_path="location", frame=frame_2)

# 2.5s: 左臂开始收回
frame_2_5 = 2.5 * frame_rate
hand_l.location += (armature.matrix_world @ (hand_l.parent.matrix if hand_l.parent else Matrix())).inverted() @ Vector((0, 0.3, 0))
hand_l.rotation_euler.x -= 0.3
hand_l.keyframe_insert(data_path="location", frame=frame_2_5)
hand_l.keyframe_insert(data_path="rotation_euler", frame=frame_2_5)

# 3.0s: 左臂回到初始位置
frame_3 = 3.0 * frame_rate
hand_l.location = (0.0, -0.5, 0.0)
hand_l.keyframe_insert(data_path="location", frame=frame_3)

