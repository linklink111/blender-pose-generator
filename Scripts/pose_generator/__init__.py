bl_info = {
    "name": "Pose Generator",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "author": "Your Name",
    "description": "A pose generator addon for Blender",
    "location": "View3D > Object",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY"
}

import bpy

def register():
    from . import operators
    from . import ui
    from . import properties

    operators.register()
    ui.register()
    properties.register()

def unregister():
    from . import operators
    from . import ui
    from . import properties

    operators.unregister()
    ui.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()