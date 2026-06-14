import bge
import bpy
import time
import math
from collections import OrderedDict

class PlayerController(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("MoveSpeed", 5.0),
        ("TurnSpeed", 0.1),
    ])

    def start(self, args):
        scene = bge.logic.getCurrentScene()
        scene.active_camera = scene.objects["Camera"]
        self._move_speed = args["MoveSpeed"]
        self._turn_speed = args["TurnSpeed"]
        self._target_angle = self.object.worldOrientation.to_euler().z

        self._last_time = time.perf_counter()
        
        self.bl_obj = bpy.data.objects.get(self.object.name)
        self.time_offset = self.bl_obj.modifiers.new(name="TIME_OFFSET", type='GREASE_PENCIL_TIME')

    def update(self):
        current_time = time.perf_counter()
        dt = current_time - self._last_time
        self._last_time = current_time

        if dt > 0.1:
            dt = 0.01666
  
        keyboard_inputs = bge.logic.keyboard.inputs
        joysticks = bge.logic.joysticks
        joystick = joysticks[0] if joysticks else None

        move_x = 0.0
        move_y = 0.0
        delta_x = 0.0
        delta_y = 0.0
        
        self.time_offset.offset = (self.time_offset.offset + 1) % 10
        
        if joystick:
            deadzone = 0.1e-4
            delta_x = joystick.axisValues[0] / 32767.0
            delta_y = -joystick.axisValues[1] / 32767.0
            if abs(delta_x) <= deadzone:
                delta_x = 0.0
            if abs(delta_y) <= deadzone:
                delta_y = 0.0        
        
        if keyboard_inputs[bge.events.WKEY].status[-1]:
#            self.object.playAction(
#                'SuzanneAction',
#                1,
#                12, 
#                layer=0,
#                play_mode=bge.logic.KX_ACTION_MODE_PLAY,
#                blend_mode=bge.logic.KX_ACTION_BLEND_ADD,
#                speed=1.0
#            )
            delta_y += 1.0
        if keyboard_inputs[bge.events.SKEY].status[-1]:
            delta_y -= 1.0
        if keyboard_inputs[bge.events.AKEY].status[-1]:
            delta_x -= 1.0
        if keyboard_inputs[bge.events.DKEY].status[-1]:
            delta_x += 1.0

        if delta_x != 0.0 or delta_y != 0.0:
            move_x += delta_x
            move_y += delta_y
            length = math.sqrt(move_x**2 + move_y**2)
            move_x /= length
            move_y /= length

            move_delta = self._move_speed * dt
            if keyboard_inputs[bge.events.LEFTSHIFTKEY].status[-1]:
                move_delta *= 2.0
                
            final_move_x = move_x * move_delta
            final_move_y = move_y * move_delta

            self.object.applyMovement([final_move_x, final_move_y, 0.0], False)
            self._target_angle = math.atan2(move_x, move_y)

        current_euler = self.object.worldOrientation.to_euler()
        current_angle = current_euler.z

        angle_diff = self._target_angle - current_angle
        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

        current_euler.z += angle_diff * self._turn_speed
        self.object.worldOrientation = current_euler