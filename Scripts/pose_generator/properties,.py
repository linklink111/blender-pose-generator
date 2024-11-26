import bpy

def register():
    bpy.types.Scene.posegen_analysis_object = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Analysis Object",
        description="Select the object for skeleton analysis"
    )

def unregister():
    del bpy.types.Scene.posegen_analysis_object