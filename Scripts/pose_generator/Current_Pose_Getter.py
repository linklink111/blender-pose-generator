import bpy
import os

# 指定文件路径
bone_mapping_file = r"E:\000CCCProject\ChatPoseBlender\blender-pose-generator\boneMapping\arp_map2"

def read_bone_mapping(file_path):
    """读取以逗号分隔的bone mapping文件"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return {}
    mapping_data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 去掉首尾空白字符并跳过空行
            line = line.strip()
            if not line:
                continue
            # 分割成键值对
            try:
                key, value = line.split(',')
                mapping_data[key.strip()] = value.strip()
            except ValueError:
                print(f"无法解析行: {line}")
    return mapping_data

def print_pose_bone_positions(bone_mapping):
    """打印Pose模式下指定关节的位置"""
    obj = bpy.context.object
    
    # 确保对象是Armature类型
    if obj.type != 'ARMATURE':
        print("当前选中的对象不是Armature类型")
        return
    
    # 切换到Pose模式
    bpy.ops.object.mode_set(mode='POSE')

    # 遍历骨骼映射并打印位置
    for joint_name, bone_name in bone_mapping.items():
        bone = obj.pose.bones.get(bone_name)
        if bone is None:
            print(f"未找到骨骼: {bone_name}")
            continue
        bone_position = bone.head  # 获取骨骼的头部位置（世界坐标）
        print(f"Joint: {joint_name}, Bone: {bone_name}, Position: {bone_position}")

# 主函数
def main():
    # 读取bone mapping
    bone_mapping = read_bone_mapping(bone_mapping_file)
    if not bone_mapping:
        print("无法读取bone mapping文件或文件内容为空")
        return

    # 打印bone mapping
    print("Bone Mapping:")
    for k, v in bone_mapping.items():
        print(f"{k}: {v}")

    # 打印Pose骨骼位置
    print("Pose Bone Positions:")
    print_pose_bone_positions(bone_mapping)

# 执行主函数
if __name__ == "__main__":
    main()
