import bpy
import xml.etree.ElementTree as ET
import mathutils

# 读取 XML 文件
xml_file_path = r"E:\000CCCProject\ChatPoseBlender\blender-pose-generator\dataset\kit-ml\2017-06-22\00001_mmm.xml"
tree = ET.parse(xml_file_path)
root = tree.getroot()

# 关节映射字典（你可以根据需求修改）
joint_mapping = {
    "LW": "c_hand_ik.l",
    "RW": "c_hand_ik.r",
    # 继续添加其他关节的映射关系
}

# 解析 MotionFrame
motion_frames = root.findall(".//MotionFrame")
frame_data = []

for motion_frame in motion_frames:
    timestep = float(motion_frame.find("Timestep").text)
    root_position = motion_frame.find("RootPosition").text.split()
    root_rotation = motion_frame.find("RootRotation").text.split()
    joint_position = motion_frame.find("JointPosition").text.split()

    frame_data.append({
        "timestep": timestep,
        "root_position": [float(val) for val in root_position],
        "root_rotation": [float(val) for val in root_rotation],
        "joint_position": [float(val) for val in joint_position]
    })

# 设置时间轴范围
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = len(frame_data)

# 在 Blender 中创建关键帧
for idx, frame in enumerate(frame_data):
    timestep = frame["timestep"]
    joint_positions = frame["joint_position"]

    # 设置当前帧
    bpy.context.scene.frame_set(idx + 1)

    # 设置根部位移和旋转
    root_obj = bpy.context.scene.objects.get("rig")  # 根据你的骨架名称修改
    #    if root_obj:
    #        root_obj.location = mathutils.Vector(frame["root_position"])
    #        root_obj.rotation_euler = mathutils.Euler(frame["root_rotation"])
    #        root_obj.keyframe_insert(data_path="location", frame=idx + 1)
    #        root_obj.keyframe_insert(data_path="rotation_euler", frame=idx + 1)

    # 设置每个关节的位置
    for i, joint_name in enumerate(joint_mapping.keys()):
        blender_bone_name = joint_mapping[joint_name]
        bone = root_obj.pose.bones.get(blender_bone_name)
        if bone:
            # 根据关节位置为每个骨骼设置位置（这里假设 joint_position 是 XYZ）
            bone.location = mathutils.Vector(joint_positions[i*3:i*3+3])  # 位置是连续的三个值
            bone.keyframe_insert(data_path="location", frame=idx + 1)

