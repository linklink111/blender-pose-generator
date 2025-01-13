import bpy
from mathutils import Vector  # 导入 Vector 类

# 确保当前对象模式是对象模式
if bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# 获取场景和 00001_raw 物体
scene = bpy.context.scene
armature_object = bpy.data.objects.get('00001_raw')

# 如果没有找到 "00001_raw" 物体，则提示并结束
if not armature_object:
    print("没有找到物体 '00001_raw'。")
    exit()

# 获取 armature 的骨骼数据
armature_data = armature_object.data

# 设置骨架名称
armature_name = "Generated_Armature"
# 创建一个空的骨架
bpy.ops.object.armature_add(enter_editmode=True)
armature = bpy.context.object
armature.name = armature_name

print("test114===============================")

# 定义目标帧
frame_number = 20

# 获取骨骼 F 曲线位置
def get_joint_position_from_fcurve(action, joint_name, frame_number):
    fcurves = action.fcurves
    x_curve = next((fc for fc in fcurves if fc.data_path == f'pose.bones["{joint_name}"].location' and fc.array_index == 0), None)
    z_curve = next((fc for fc in fcurves if fc.data_path == f'pose.bones["{joint_name}"].location' and fc.array_index == 1), None)
    y_curve = next((fc for fc in fcurves if fc.data_path == f'pose.bones["{joint_name}"].location' and fc.array_index == 2), None)

    if x_curve and y_curve and z_curve:
        x = x_curve.evaluate(frame_number)
        y = -y_curve.evaluate(frame_number)
        z = z_curve.evaluate(frame_number)
        return Vector((x, y, z))
    else:
        print(f"没有找到关节 {joint_name} 的 F 曲线")
        return None

# 获取动画动作
action = armature_object.animation_data.action
if not action:
    print(f"骨架 {armature_object.name} 没有绑定动作")
    exit()

# 创建骨骼层级结构
joint_hierarchy = [
    ['L3', 'T10', 'C7', 'LSHO', 'LAEL', 'LWPS', 'LHPS'],
    ['C7', 'RSHO', 'RAEL', 'RWPS', 'RHPS'],
    ['C7', 'LBHD'],
    ['C7', 'RBHD'],
    ['L3', 'LASI', 'LKNE', 'LHEE', 'LANK', 'LTOE'],
    ['L3', 'RASI', 'RKNE', 'RHEE', 'RANK', 'RTOE']
]

# 查找骨骼的父级
def find_parent_bone(joint, joint_hierarchy, created_bones):
    for hierarchy in joint_hierarchy:
        if joint in hierarchy and hierarchy.index(joint) > 0:  # 骨骼在层级中但不是第一个
            parent_joint = hierarchy[hierarchy.index(joint) - 1]
            return created_bones.get(parent_joint)  # 返回已创建的骨骼
    return None

# 创建骨架的骨骼（joint）
created_bones = {}  # 存储已创建的骨骼 {joint_name: bone}
for hierarchy in joint_hierarchy:
    previous_bone = None
    for i, joint in enumerate(hierarchy):
        # 如果没有下一个关节，跳过当前关节
        if i + 1 >= len(hierarchy):
            print(f"关节 {joint} 是末端关节，不创建骨骼。")
            continue

        # 获取当前关节的坐标
        joint_position = get_joint_position_from_fcurve(action, joint, frame_number)
        if not joint_position:
            print(f"没有找到关节: {joint}")
            continue

        # 获取下一个关节的位置，作为当前骨骼的尾部位置
        next_joint = hierarchy[i + 1]
        next_joint_position = get_joint_position_from_fcurve(action, next_joint, frame_number)
        if not next_joint_position:
            print(f"没有找到下一个关节: {next_joint}")
            continue

        # 创建一个新的骨骼
        print(f"创建骨骼: {joint} -> {next_joint}")
        bone = armature.data.edit_bones.new(next_joint)
        bone.head = joint_position
        bone.tail = next_joint_position

        # 如果是当前层级的第一个骨骼，检查是否需要连接到其他层级的末端
        if i == 0:
            parent_bone = find_parent_bone(joint, joint_hierarchy, created_bones)
            if parent_bone:
                bone.parent = parent_bone
                print(f"骨骼 {joint} 被连接到其他层级骨骼 {parent_bone.name} 的末端。")

        # 设置普通的父骨骼关系
        if previous_bone:
            bone.parent = previous_bone

        # 记录已创建的骨骼
        created_bones[joint] = bone
        previous_bone = bone

# 退出编辑模式，保存骨架
bpy.ops.object.mode_set(mode='OBJECT')

# 添加修改器
for bone_name in armature.pose.bones.keys():
    pose_bone = armature.pose.bones[bone_name]

    # 检查骨骼名称是否为 T10、RASI 或 LASI
    if bone_name in ["T10", "RASI", "LASI"]:
        # 添加 Copy Location 修改器
        constraint = pose_bone.constraints.new(type='COPY_LOCATION')
        constraint.target = armature_object
        constraint.subtarget = "L3"  # 目标是 00001_raw 的 L3
        print(f"为骨骼 {bone_name} 添加 Copy Location 修改器，目标为关节 L3")
    else:
        # 添加 Damped Track 修改器
        constraint = pose_bone.constraints.new(type='DAMPED_TRACK')
        constraint.target = armature_object
        constraint.subtarget = bone_name  # 使用骨骼名（对应目标关节名）作为 subtarget
        print(f"为骨骼 {bone_name} 添加 Damped Track 修改器，目标为关节 {bone_name}")

# 确保骨架对象被选中
armature.select_set(True)



