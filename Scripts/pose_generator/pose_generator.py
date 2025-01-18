import bpy
from mathutils import Vector
import csv
import os
import json
import requests
import logging
from datetime import datetime

# CSV文件路径
CSV_FILE_PATH = "path/to/your/bone_mapping.csv"
HOST_NAME = "localhost"
PORT = 5000

# 创建日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建文件处理器
LOG_FILE_PATH = f"log_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)

# 添加日志记录到终端（可选）
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 打印日志文件的位置
print(f"Log file created at: {LOG_FILE_PATH}")

# 插件启动时输出“start running”
logger.info("Start running")

# 定义一个枚举属性，用于控制选项卡的选择
def update_page(self, context):
    pass

bpy.types.Scene.page_selection = bpy.props.EnumProperty(
    name="Page",
    items=[
        ('ANALYSIS', "Analysis", "Skeleton Analysis Work Area"),
        ('GENERATE', "Generate", "Generate Pose Work Area"),
        ('EDIT', "Edit", "Edit Pose Work Area"),
    ],
    default='ANALYSIS',
    update=update_page
)

class POSEGEN_BoneMappingItem(bpy.types.PropertyGroup):
    common_name: bpy.props.StringProperty(name="Common Name", default="")
    bone_name: bpy.props.StringProperty(name="Bone Name", default="")

class POSEGEN_UL_BoneMappingList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, "common_name", text="", emboss=False, icon_value=icon)
            row.prop(item, "bone_name", text="", emboss=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class POSEGEN_PT_PoseGeneratorPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Pose Generator"
    bl_idname = "POSEGEN_PT_pose_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Pose Generator'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 创建选项卡
        row = layout.row()
        row.prop(scene, "page_selection", expand=True)

        # 根据选中的选项卡显示不同的内容
        if scene.page_selection == 'ANALYSIS':
            # Skeleton Analysis Work Area
            box = layout.box()
            box.label(text="Skeleton Analysis Work Area")

            row = box.row()
            row.prop(context.scene, "posegen_analysis_object", text="Select Object")
            row.operator("posegen.analysis", text="Analysis")

            row = box.row()
            row.template_list("POSEGEN_UL_BoneMappingList", "", context.scene, "posegen_bone_mapping", context.scene, "posegen_bone_mapping_index")

            row = box.row()
            row.operator("posegen.load_mapping", text="Load Mapping")
            row.operator("posegen.add_mapping", text="Add Mapping")
            row.operator("posegen.remove_mapping", text="Remove Mapping").index = context.scene.posegen_bone_mapping_index
            row.operator("posegen.save_mapping", text="Save Mapping")

        elif scene.page_selection == 'GENERATE':
            # Generate Pose Work Area
            box = layout.box()
            box.label(text="Generate Pose Work Area")
            
            row = box.row()
            row.operator("posegen.clear_pose", text="Clear Pose")  # Add this line
            row = box.row()
            row.operator("posegen.clear_animation", text="Clear Animation")  # 添加 Clear Animation 按钮

            row = box.row()
            row.prop(context.scene, "posegen_prompt", text="Prompt", icon='TEXT')
            
            row = box.row()
            row.operator("posegen.generate_pose", text="Generate Pose")
            
            
            
            # Pose Design 结果列表
            box = layout.box()
            box.label(text="Pose Design Results")
            
            row = box.row()
            row.template_list("POSEGEN_UL_PoseDesignList", "", context.scene, "posegen_pose_design_items", context.scene, "posegen_pose_design_index")
            
            # 添加 Pose Design 按钮
            row = box.row()
            row.operator("posegen.design_pose", text="Pose Design")
            
            # Add / Remove buttons for Pose Design
            row = box.row()
            row.operator("posegen.add_pose_design", text="Add Pose Design")
            row.operator("posegen.remove_pose_design", text="Remove Pose Design")
            
            # Generate All / Generate Selected buttons
            row = box.row()
            row.operator("posegen.generate_all_poses", text="Generate All")
            row.operator("posegen.generate_selected_pose", text="Generate Selected")

            # Add Detect All and Detect Selected buttons
            row = box.row()
            row.operator("posegen.detect_all", text="Detect All")
            row.operator("posegen.detect_selected", text="Detect Selected")
            # Add Refine All and Refine Selected buttons
            row = box.row()
            row.operator("posegen.refine_all", text="Refine All")
            row.operator("posegen.refine_selected", text="Refine Selected")



        elif scene.page_selection == 'EDIT':
            # Edit Pose Work Area
            box = layout.box()
            box.label(text="Edit Pose Work Area")
            
            row = box.row()
            row.prop(context.scene, "posegen_edit_prompt", text="Prompt", icon='TEXT')
            
            row = box.row()
            row.operator("posegen.edit_pose", text="Edit Pose")

def register():
    bpy.utils.register_class(POSEGEN_BoneMappingItem)
    bpy.utils.register_class(POSEGEN_UL_BoneMappingList)
    
    bpy.types.Scene.posegen_prompt = bpy.props.StringProperty(
        name="Generate Prompt",
        description="Enter the prompt for generating a pose",
        default="",
        maxlen=1024,
    )
    
    bpy.types.Scene.posegen_edit_prompt = bpy.props.StringProperty(
        name="Edit Prompt",
        description="Enter the prompt for editing a pose",
        default="",
        maxlen=1024,
    )
    
    bpy.types.Scene.posegen_analysis_object = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Analysis Object",
        description="Select the object for skeleton analysis"
    )
    
    bpy.types.Scene.posegen_bone_mapping = bpy.props.CollectionProperty(
        type=POSEGEN_BoneMappingItem
    )
    
    bpy.types.Scene.posegen_bone_mapping_index = bpy.props.IntProperty(name="Index for bone mapping list", default=0)
    
    bpy.utils.register_class(POSEGEN_PT_PoseGeneratorPanel)
    
    # Register operators
    bpy.utils.register_class(POSEGEN_OT_GeneratePose)
    bpy.utils.register_class(POSEGEN_OT_DesignPose)
    bpy.utils.register_class(POSEGEN_PoseDesignItem)
    bpy.utils.register_class(POSEGEN_UL_PoseDesignList)
    bpy.utils.register_class(POSEGEN_OT_AddPoseDesign)
    bpy.utils.register_class(POSEGEN_OT_RemovePoseDesign)
    bpy.utils.register_class(POSEGEN_OT_GenerateAllPoseDesigns)
    bpy.utils.register_class(POSEGEN_OT_GenerateSelectedPoseDesign)
    bpy.utils.register_class(POSEGEN_OT_EditPose)
    bpy.utils.register_class(POSEGEN_OT_Analysis)
    bpy.utils.register_class(POSEGEN_OT_AddMapping)
    bpy.utils.register_class(POSEGEN_OT_RemoveMapping)
    bpy.utils.register_class(POSEGEN_OT_SaveMapping)
    bpy.utils.register_class(POSEGEN_OT_LoadMapping)
    bpy.utils.register_class(POSEGEN_OT_ClearPose)  # Add this line
    bpy.utils.register_class(POSEGEN_OT_ClearAnimation)  # 注册新的操作符
    bpy.utils.register_class(POSEGEN_OT_DetectAll)
    bpy.utils.register_class(POSEGEN_OT_DetectSelected)
    bpy.utils.register_class(POSEGEN_OT_RefineAll)
    bpy.utils.register_class(POSEGEN_OT_RefineSelected)
    
    bpy.types.Scene.posegen_pose_design_items = bpy.props.CollectionProperty(type=POSEGEN_PoseDesignItem)
    bpy.types.Scene.posegen_pose_design_index = bpy.props.IntProperty(name="Index for pose design list", default=0)

    # Load bone mapping from CSV file
    load_bone_mapping_from_csv()

def unregister():
    del bpy.types.Scene.posegen_prompt
    del bpy.types.Scene.posegen_edit_prompt
    del bpy.types.Scene.posegen_analysis_object
    del bpy.types.Scene.posegen_bone_mapping
    del bpy.types.Scene.posegen_bone_mapping_index
    
    bpy.utils.unregister_class(POSEGEN_PT_PoseGeneratorPanel)
    
    # Unregister operators
    bpy.utils.unregister_class(POSEGEN_OT_GeneratePose)
    bpy.utils.unregister_class(POSEGEN_OT_DesignPose)
    bpy.utils.unregister_class(POSEGEN_PoseDesignItem)
    bpy.utils.unregister_class(POSEGEN_UL_PoseDesignList)
    bpy.utils.unregister_class(POSEGEN_OT_AddPoseDesign)
    bpy.utils.unregister_class(POSEGEN_OT_RemovePoseDesign)
    bpy.utils.unregister_class(POSEGEN_OT_GenerateAllPoseDesigns)
    bpy.utils.unregister_class(POSEGEN_OT_GenerateSelectedPoseDesign)
    bpy.utils.unregister_class(POSEGEN_OT_EditPose)
    bpy.utils.unregister_class(POSEGEN_OT_Analysis)
    bpy.utils.unregister_class(POSEGEN_OT_AddMapping)
    bpy.utils.unregister_class(POSEGEN_OT_RemoveMapping)
    bpy.utils.unregister_class(POSEGEN_OT_SaveMapping)
    bpy.utils.unregister_class(POSEGEN_OT_LoadMapping)
    bpy.utils.unregister_class(POSEGEN_OT_ClearPose)  # Add this line
    bpy.utils.unregister_class(POSEGEN_OT_ClearAnimation)  # 取消注册
    bpy.utils.unregister_class(POSEGEN_OT_DetectAll)
    bpy.utils.unregister_class(POSEGEN_OT_DetectSelected)
    bpy.utils.unregister_class(POSEGEN_OT_RefineAll)
    bpy.utils.unregister_class(POSEGEN_OT_RefineSelected)

    bpy.utils.unregister_class(POSEGEN_BoneMappingItem)
    bpy.utils.unregister_class(POSEGEN_UL_BoneMappingList)



class POSEGEN_OT_GeneratePose(bpy.types.Operator):
    """Generate a new pose based on the prompt"""
    bl_idname = "posegen.generate_pose"
    bl_label = "Generate Pose"

    def execute(self, context):
        prompt = context.scene.posegen_prompt
        logging.info(f"Generating pose with prompt: {prompt}")
        self.report({'INFO'}, f"Generating pose with prompt: {prompt}")

        # 获取选定的骨架对象
        obj = context.scene.posegen_analysis_object
        if obj and obj.type == 'ARMATURE':
            # 发送请求到服务器
            try:
                response = requests.post(f'http://{HOST_NAME}:{PORT}/generate_pose', json={'prompt': prompt})
                response.raise_for_status()
                response_data = response.json()

                # 提取手部、脚部和臀部移动的指令
                hand_instructions = response_data.get('hand_instructions', [])
                foot_instructions = response_data.get('foot_instructions', [])
                hip_instructions = response_data.get('hip_instructions', [])

                # 记录指令到日志
                logging.info(f"Hand instructions: {hand_instructions}")
                logging.info(f"Foot instructions: {foot_instructions}")
                logging.info(f"Hip instructions: {hip_instructions}")

                # 这里可以添加更多的逻辑来应用这些指令
                # 例如，根据指令调整骨骼的位置

            except requests.RequestException as e:
                logging.error(f"Error communicating with server: {e}")
                self.report({'ERROR'}, f"Error communicating with server: {e}")
        else:
            logging.warning("Please select an armature object")
            self.report({'WARNING'}, "Please select an armature object")

        return {'FINISHED'}

class POSEGEN_PoseDesignItem(bpy.types.PropertyGroup):
    time: bpy.props.FloatProperty(name="Time", description="Time in seconds", default=0.0)
    description: bpy.props.StringProperty(name="Description", description="Description of the pose at this time", default="")

class POSEGEN_UL_PoseDesignList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Displaying the time and description
        row = layout.row()
        row.prop(item, "time", text="Time", emboss=False)
        row.prop(item, "description", text="Description", emboss=False)

class POSEGEN_OT_AddPoseDesign(bpy.types.Operator):
    """Add a new pose design item"""
    bl_idname = "posegen.add_pose_design"
    bl_label = "Add Pose Design"

    def execute(self, context):
        item = context.scene.posegen_pose_design_items.add()
        item.time = 0.0
        item.description = "New Pose"
        context.scene.posegen_pose_design_index = len(context.scene.posegen_pose_design_items) - 1
        logging.info("Added new pose design item")
        return {'FINISHED'}

class POSEGEN_OT_RemovePoseDesign(bpy.types.Operator):
    """Remove a pose design item"""
    bl_idname = "posegen.remove_pose_design"
    bl_label = "Remove Pose Design"

    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.posegen_pose_design_items.remove(self.index)
        context.scene.posegen_pose_design_index = min(max(0, self.index - 1), len(context.scene.posegen_pose_design_items) - 1)
        logging.info(f"Removed pose design item at index {self.index}")
        return {'FINISHED'}

class POSEGEN_OT_GenerateAllPoseDesigns(bpy.types.Operator):
    """Generate all poses in the Pose Design list"""
    bl_idname = "posegen.generate_all_poses"
    bl_label = "Generate All"

    def execute(self, context):
        # 遍历 Pose Design 列表中的所有条目并生成相应的动作
        pose_designs = context.scene.posegen_pose_design_items
        for item in pose_designs:
            logging.info(f"Generating pose at {item.time}s: {item.description}")
            # 你可以在这里添加生成每个姿势的具体逻辑
        self.report({'INFO'}, "Generated all poses")
        return {'FINISHED'}

class POSEGEN_OT_GenerateSelectedPoseDesign(bpy.types.Operator):
    """Generate selected pose in the Pose Design list"""
    bl_idname = "posegen.generate_selected_pose"
    bl_label = "Generate Selected"

    def execute(self, context):
        # 获取当前选中的 Pose Design 条目
        selected_index = context.scene.posegen_pose_design_index
        pose_design_items = context.scene.posegen_pose_design_items

        if selected_index < 0 or selected_index >= len(pose_design_items):
            self.report({'WARNING'}, "No pose selected!")
            return {'CANCELLED'}

        selected_item = pose_design_items[selected_index]
        logging.info(f"Generating selected pose for: {selected_item.description}")

        # 获取骨骼世界坐标
        armature_name = "rig"  # 替换为你的实际骨架名称
        bone_mapping = {
            "left_hand": "c_hand_ik.l",
            "right_hand": "c_hand_ik.r",
            "left_foot": "c_foot_ik.l",
            "right_foot": "c_foot_ik.r",
            "hip": "c_root_master.x",
            "left_elbow": "c_arms_pole.l",
            "right_elbow": "c_arms_pole.r",
            "left_knee": "c_leg_pole.l",
            "right_knee": "c_leg_pole.r",
            "head": "c_head.x",
            "chest": "c_spine_02.x",
            "waist": "c_spine_01.x",
            "neck" :"c_neck.x"
        }

        try:
            bone_world_positions = get_bone_world_positions(armature_name, bone_mapping, int(selected_item.time*24))
            print(bone_world_positions)
            if bone_world_positions is None:
                self.report({'ERROR'}, "Failed to retrieve bone world positions.")
                return {'CANCELLED'}

            # 构建请求数据
            data = {
                "time": selected_item.time,
                "pose_description": selected_item.description,
                "body_world_pos": bone_world_positions  # 添加骨骼世界坐标数据
            }

            # 发送请求到服务器
            url = f"http://{HOST_NAME}:{PORT}/api/post_generate_pose_code"
            response = requests.post(url, json=data)
            response.raise_for_status()

            # 获取返回的代码
            response_data = response.json()
            pose_code = response_data.get("data")
            print(pose_code)

            if not pose_code:
                self.report({'ERROR'}, "Server did not return any code.")
                return {'CANCELLED'}

            # 在 Blender 的脚本编辑器中运行代码
            exec(pose_code, {"bpy": bpy})
            self.report({'INFO'}, "Pose generated and executed successfully.")
            logging.info("Pose script executed successfully.")

        except requests.RequestException as e:
            logging.error(f"Error communicating with server: {e}")
            self.report({'ERROR'}, f"Error communicating with server: {e}")
        except Exception as e:
            logging.error(f"Error executing pose script: {e}")
            self.report({'ERROR'}, f"Error executing pose script: {e}")

        return {'FINISHED'}



# 新增操作符 Pose Design
class POSEGEN_OT_DesignPose(bpy.types.Operator):
    """Design a new pose based on user input"""
    bl_idname = "posegen.design_pose"
    bl_label = "Design Pose"

    def execute(self, context):
        # 获取输入框的文本内容
        prompt = context.scene.posegen_prompt

        if not prompt.strip():
            self.report({'ERROR'}, "Prompt cannot be empty!")
            return {'CANCELLED'}

        # API 的 URL 和参数
        url = "http://127.0.0.1:5000/api/post_generate_pose_design"
        data = {"user_prompt": prompt}
        
        try:
            # 发送 POST 请求
            response = requests.post(url, json=data)
            response_data = response.json()

            if response.status_code == 201 and response_data.get("status") == "success":
                # 解析返回的数据
                pose_list = json.loads(response_data["data"])

                print(pose_list)
                
                # 清空现有的 Pose Design List
                context.scene.posegen_pose_design_items.clear()

                # 将解析后的数据添加到列表中
                for pose in pose_list:
                    new_item = context.scene.posegen_pose_design_items.add()
                    new_item.time = pose["time"]
                    new_item.description = pose["pose"]

                # 显示成功消息
                self.report({'INFO'}, response_data.get("message", "Pose design generated successfully."))
                return {'FINISHED'}
            else:
                # API 错误处理
                self.report({'ERROR'}, f"API Error: {response_data.get('message', 'Unknown error')}")
                return {'CANCELLED'}

        except Exception as e:
            # 请求失败时的错误处理
            self.report({'ERROR'}, f"Request failed: {str(e)}")
            return {'CANCELLED'}
    
class POSEGEN_OT_ClearPose(bpy.types.Operator):
    """Clear the current pose"""
    bl_idname = "posegen.clear_pose"
    bl_label = "Clear Pose"

    def execute(self, context):
        obj = context.scene.posegen_analysis_object
        if obj and obj.type == 'ARMATURE':
            # Reset all bone positions to their default (rest) position
            for bone in obj.pose.bones:
                bone.location = (0, 0, 0)
                bone.rotation_quaternion = (1, 0, 0, 0)
                bone.scale = (1, 1, 1)
            logging.info("Pose cleared")
            self.report({'INFO'}, "Pose cleared")
        else:
            logging.warning("Please select an armature object")
            self.report({'WARNING'}, "Please select an armature object")
        return {'FINISHED'}

class POSEGEN_OT_EditPose(bpy.types.Operator):
    """Edit an existing pose based on the prompt"""
    bl_idname = "posegen.edit_pose"
    bl_label = "Edit Pose"

    def execute(self, context):
        prompt = context.scene.posegen_edit_prompt
        logging.info(f"Editing pose with prompt: {prompt}")
        self.report({'INFO'}, f"Editing pose with prompt: {prompt}")
        # Add your pose editing logic here
        return {'FINISHED'}

class POSEGEN_OT_Analysis(bpy.types.Operator):
    """Analyze the selected object's skeleton"""
    bl_idname = "posegen.analysis"
    bl_label = "Analysis"

    def execute(self, context):
        obj = context.scene.posegen_analysis_object
        if obj and obj.type == 'ARMATURE':
            logging.info(f"Analyzing skeleton of object: {obj.name}")
            self.report({'INFO'}, f"Analyzing skeleton of object: {obj.name}")
            
            # Get all bone names
            bone_names = [bone.name for bone in obj.data.bones]
            logger.info(f"Sending bone data: {bone_names}")
            
            # Send request to server
            try:
                response = requests.post('http://{}:{}/analyze_skeleton'.format(HOST_NAME,PORT), json={'bone_names': bone_names})
                response.raise_for_status()
                csv_text = response.text
                
                # Parse CSV text and add to bone mapping
                bone_mapping = context.scene.posegen_bone_mapping
                bone_mapping.clear()
                
                reader = csv.reader(csv_text.splitlines())
                for row in reader:
                    if len(row) == 2:
                        item = bone_mapping.add()
                        item.common_name = row[0]
                        item.bone_name = row[1]
                
                logging.info("Bone mapping loaded from server")
                self.report({'INFO'}, "Bone mapping loaded from server")
            except requests.RequestException as e:
                logging.error(f"Error communicating with server: {e}")
                self.report({'ERROR'}, f"Error communicating with server: {e}")
        else:
            logging.warning("Please select an armature object")
            self.report({'WARNING'}, "Please select an armature object")
        return {'FINISHED'}

class POSEGEN_OT_AddMapping(bpy.types.Operator):
    """Add a new bone mapping item"""
    bl_idname = "posegen.add_mapping"
    bl_label = "Add Mapping"

    def execute(self, context):
        item = context.scene.posegen_bone_mapping.add()
        item.common_name = "New Common Name"
        item.bone_name = "New Bone Name"
        context.scene.posegen_bone_mapping_index = len(context.scene.posegen_bone_mapping) - 1
        logging.info("Added new bone mapping item")
        return {'FINISHED'}

class POSEGEN_OT_RemoveMapping(bpy.types.Operator):
    """Remove a bone mapping item"""
    bl_idname = "posegen.remove_mapping"
    bl_label = "Remove Mapping"

    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.posegen_bone_mapping.remove(self.index)
        context.scene.posegen_bone_mapping_index = min(max(0, self.index - 1), len(context.scene.posegen_bone_mapping) - 1)
        logging.info(f"Removed bone mapping item at index {self.index}")
        return {'FINISHED'}

class POSEGEN_OT_SaveMapping(bpy.types.Operator):
    """Save bone mapping to CSV file"""
    bl_idname = "posegen.save_mapping"
    bl_label = "Save Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.filepath:
            logging.error("No file path specified")
            self.report({'ERROR'}, "No file path specified")
            return {'CANCELLED'}

        bone_mapping = context.scene.posegen_bone_mapping

        try:
            with open(self.filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                for mapping in bone_mapping:
                    writer.writerow([mapping.common_name, mapping.bone_name])
            logging.info(f"Bone mapping saved to {self.filepath}")
            self.report({'INFO'}, f"Bone mapping saved to {self.filepath}")
        except Exception as e:
            logging.error(f"Error saving file: {e}")
            self.report({'ERROR'}, f"Error saving file: {e}")

        return {'FINISHED'}

class POSEGEN_OT_LoadMapping(bpy.types.Operator):
    """Load bone mapping from a CSV file"""
    bl_idname = "posegen.load_mapping"
    bl_label = "Load Mapping"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not os.path.exists(self.filepath):
            logging.error("File does not exist")
            self.report({'ERROR'}, "File does not exist")
            return {'CANCELLED'}

        bone_mapping = context.scene.posegen_bone_mapping
        bone_mapping.clear()

        with open(self.filepath, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:
                    item = bone_mapping.add()
                    item.common_name = row[0]
                    item.bone_name = row[1]

        logging.info(f"Bone mapping loaded from {self.filepath}")
        self.report({'INFO'}, f"Bone mapping loaded from {self.filepath}")
        return {'FINISHED'}
    
class POSEGEN_OT_ClearAnimation(bpy.types.Operator):
    """Clear all animations from the selected object"""
    bl_idname = "posegen.clear_animation"
    bl_label = "Clear Animation"

    def execute(self, context):
        obj = context.scene.posegen_analysis_object
        if obj:
            # Clear animation data if it exists
            if obj.animation_data:
                obj.animation_data_clear()
                logging.info(f"Animation data cleared for object: {obj.name}")
                self.report({'INFO'}, f"Animation data cleared for object: {obj.name}")
            else:
                logging.warning(f"No animation data found for object: {obj.name}")
                self.report({'WARNING'}, f"No animation data found for object: {obj.name}")
        else:
            logging.warning("Please select an object")
            self.report({'WARNING'}, "Please select an object")
        return {'FINISHED'}

class POSEGEN_OT_DetectAll(bpy.types.Operator):
    bl_idname = "posegen.detect_all"
    bl_label = "Detect All"
    bl_description = "Detect anomalies in all poses"

    def execute(self, context):
        # 在这里添加检测所有姿势的逻辑
        self.report({'INFO'}, "Detect All executed")
        return {'FINISHED'}

class POSEGEN_OT_DetectSelected(bpy.types.Operator):
    bl_idname = "posegen.detect_selected"
    bl_label = "Detect Selected"
    bl_description = "Detect anomalies in selected poses"

    def execute(self, context):
        # 在这里添加检测选定姿势的逻辑
        self.report({'INFO'}, "Detect Selected executed")
        return {'FINISHED'}

class POSEGEN_OT_RefineAll(bpy.types.Operator):
    bl_idname = "posegen.refine_all"
    bl_label = "Refine All"
    bl_description = "Refine all poses"

    def execute(self, context):
        # 在这里添加精炼所有姿势的逻辑
        self.report({'INFO'}, "Refine All executed")
        return {'FINISHED'}

class POSEGEN_OT_RefineSelected(bpy.types.Operator):
    bl_idname = "posegen.refine_selected"
    bl_label = "Refine Selected"
    bl_description = "Refine selected poses"

    def execute(self, context):
        # 在这里添加精炼选定姿势的逻辑
        self.report({'INFO'}, "Refine Selected executed")
        return {'FINISHED'}
def load_bone_mapping_from_csv():
    if not os.path.exists(CSV_FILE_PATH):
        logging.warning("CSV file does not exist")
        return

    context = bpy.context
    bone_mapping = context.scene.posegen_bone_mapping
    bone_mapping.clear()

    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                item = bone_mapping.add()
                item.common_name = row[0]
                item.bone_name = row[1]

    logging.info(f"Bone mapping loaded from {CSV_FILE_PATH}")


def get_bone_world_positions(armature_name, bone_mapping, frame):
    obj = bpy.data.objects.get(armature_name)
    if obj is None or obj.type != 'ARMATURE':
        return None

    bone_world_positions = {}

    for key, bone_name in bone_mapping.items():
        pose_bone = obj.pose.bones.get(bone_name)
        if not pose_bone:
            continue

        bone_world_pos = Vector((0.0, 0.0, 0.0))
        has_data = False

        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                data_path = fcurve.data_path
                if data_path.startswith(f'pose.bones["{bone_name}"].location'):
                    index = fcurve.array_index
                    bone_world_pos[index] = fcurve.evaluate(frame)
                    has_data = True

        if not has_data:
            # 如果没有fcurve数据，直接获取世界坐标
            bone_world_pos = pose_bone.location

        # 将局部坐标转换为世界坐标
        local_matrix = pose_bone.matrix_basis.copy()
        local_matrix.translation = bone_world_pos
        world_matrix = obj.matrix_world @ pose_bone.bone.matrix_local @ local_matrix
        bone_world_positions[key] = [round(coord, 2) for coord in world_matrix.translation]

        print(f"Bone {key}: {bone_world_positions[key]}")

    return bone_world_positions

if __name__ == "__main__":
    register()