import bpy
from mathutils import Vector

# 获取动作对象
armature_name = "00001_raw"  # 替换为你的骨架名称
bone_name = "T10"  # 骨骼名称
frame_number = 20  # 目标帧号

# 获取骨架对象
armature = bpy.data.objects.get(armature_name)
if not armature:
    print(f"没有找到骨架对象: {armature_name}")
    exit()

# 获取动作
action = armature.animation_data.action
if not action:
    print(f"骨架 {armature_name} 没有绑定动作")
    exit()

# 获取骨骼的位置动画 F 曲线
fcurves = action.fcurves
x_curve = next((fc for fc in fcurves if fc.data_path == f'pose.bones["{bone_name}"].location' and fc.array_index == 0), None)
y_curve = next((fc for fc in fcurves if fc.data_path == f'pose.bones["{bone_name}"].location' and fc.array_index == 1), None)
z_curve = next((fc for fc in fcurves if fc.data_path == f'pose.bones["{bone_name}"].location' and fc.array_index == 2), None)

# 确保 F 曲线存在
if not x_curve or not y_curve or not z_curve:
    print(f"没有找到骨骼 {bone_name} 的 F 曲线")
    exit()

# 评估第 20 帧的位置
x = x_curve.evaluate(frame_number)
y = y_curve.evaluate(frame_number)
z = z_curve.evaluate(frame_number)
position = Vector((x, y, z))

# 打印结果
print(f"骨骼 {bone_name} 在第 {frame_number} 帧的位置: {position}")
