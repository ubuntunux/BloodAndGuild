import bge
import time
import math
from collections import OrderedDict

class PlayerController(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("MoveSpeed", 5.0),
        ("TurnSpeed", 0.1),
    ])

    def start(self, args):
        self._move_speed = args["MoveSpeed"]
        self._turn_speed = args["TurnSpeed"]
        self._target_angle = self.object.worldOrientation.to_euler().z

        self._last_time = time.perf_counter()

    def update(self):
        current_time = time.perf_counter()
        dt = current_time - self._last_time
        self._last_time = current_time

        if dt > 0.1:
            dt = 0.01666
  
        keyboard_inputs = bge.logic.keyboard.inputs
        joysticks = bge.logic.joysticks

        move_x = 0.0
        move_y = 0.0
        
        if joysticks:            
            deadzone = 0.1e-4
            joy = joysticks[0]
            delta_x = joy.axisValues[0] / 32767.0
            delta_y = -joy.axisValues[1] / 32767.0
            if abs(delta_x) <= deadzone:
                delta_x = 0.0
            if abs(delta_y) <= deadzone:
                delta_y = 0.0
            
        if keyboard_inputs[bge.events.WKEY].status[-1]:
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