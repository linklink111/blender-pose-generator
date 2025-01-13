import bpy
import csv
import os
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
LOG_FILE_PATH = f"E:/000CCCProject/ChatPoseBlender/blender-pose-generator/run/logs/log_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
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
    bpy.utils.register_class(POSEGEN_OT_EditPose)
    bpy.utils.register_class(POSEGEN_OT_Analysis)
    bpy.utils.register_class(POSEGEN_OT_AddMapping)
    bpy.utils.register_class(POSEGEN_OT_RemoveMapping)
    bpy.utils.register_class(POSEGEN_OT_SaveMapping)
    bpy.utils.register_class(POSEGEN_OT_LoadMapping)
    bpy.utils.register_class(POSEGEN_OT_ClearPose)  # Add this line
    bpy.utils.register_class(POSEGEN_OT_ClearAnimation)  # 注册新的操作符

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
    bpy.utils.unregister_class(POSEGEN_OT_EditPose)
    bpy.utils.unregister_class(POSEGEN_OT_Analysis)
    bpy.utils.unregister_class(POSEGEN_OT_AddMapping)
    bpy.utils.unregister_class(POSEGEN_OT_RemoveMapping)
    bpy.utils.unregister_class(POSEGEN_OT_SaveMapping)
    bpy.utils.unregister_class(POSEGEN_OT_LoadMapping)
    bpy.utils.unregister_class(POSEGEN_OT_ClearPose)  # Add this line
    bpy.utils.unregister_class(POSEGEN_OT_ClearAnimation)  # 取消注册

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

if __name__ == "__main__":
    register()