from kivy.config import Config

Config.set("input", "mouse", "mouse,disable_multitouch")

import math

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Mesh
from kivy.properties import ListProperty, NumericProperty, ColorProperty

from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.instructions import InstructionGroup

from pathlib import Path

from kivy.metrics import dp

"""
    Rules:
    1. All the work is to be done in numeric coordinates and only convert them to pixels when updating the mesh
       Or the drawing

    2. Everything will be in reference to two vars: x_min, x_max
       x_min will denote the smallest tick on the screen

    3. Panning: For panning I will store two values : dx, dy, which represent how much the user has panned the screen
       along x and along y. for example, say x_min right now is -10, dx = 5, new x_min = -5, capiche?
       also if dx or dy are not integers, again, for example, y_min = -6, dy = -0.3 => y_min = -6.3, we will start from -6.3
       but obv depending on the current zoom scale, it may or maynot show up as a major tick

    4. Zooming: Not sure yet but we do have to keep record of some scale amount, which will be 1x by default
       and change the steps, x_min, based on that, not yet sure tho

    5. Make sure x_min, y_min and max version are always integers

    6. Unit calculation:
        - (x_max - x_min) -> total step,
        - log10(x_min - x_max)
        -
"""


class CartesianCoordinateSystem(StencilView, Widget):
    origin_x = NumericProperty(0)
    origin_y = NumericProperty(0)

    x_min = NumericProperty(0)
    x_max = NumericProperty(0)
    y_min = NumericProperty(0)
    y_max = NumericProperty(0)
    unit_x = NumericProperty(0)
    unit_y = NumericProperty(0)
    unit_minor_x = NumericProperty(0)
    unit_minor_y = NumericProperty(0)
    precision = NumericProperty(0)

    d_x = NumericProperty(0)
    d_y = NumericProperty(0)

    scale_factor = NumericProperty(0)
    major_tick_size = NumericProperty(0)

    cursor_pos_before_zoom = ListProperty(0)
    cursor_coords_before_zoom = ListProperty(0)

    label_widgets = InstructionGroup()


    def get_origin_x(self):
        return self.x + self.width / 2 + self.d_x


    def get_origin_y(self):
        return self.y + self.height / 2 + self.d_y
    

    def point_to_pixel(self, point, sf=None):

        if sf == None:
            sf = self.scale_factor

        pixelx = point[0] * self.major_tick_size * sf + self.origin_x
        pixely = point[1] * self.major_tick_size * sf + self.origin_y
        return [round(pixelx), round(pixely)]
    

    def pixel_to_point(self, pixel, sf=None):

        if sf == None:
            sf = self.scale_factor

        pointx = (pixel[0] - self.origin_x) / (self.major_tick_size * sf)
        pointy = (pixel[1] - self.origin_y) / (self.major_tick_size * sf)
        return [pointx, pointy]
    

    def on_touch_move(self, touch):

        if not self.collide_point(*touch.pos):
            return super().on_touch_move(touch)

        self.on_panning(touch.dx, touch.dy)


    def on_touch_down(self, touch):

        if touch.is_mouse_scrolling:
            print("zoom detected")
            self.handle_zoom(touch)


    def handle_zoom(self, touch):
        cursor_pos_before_zoom = touch.pos
        cursor_coords_before_zoom = self.pixel_to_point(cursor_pos_before_zoom)

        if touch.button not in ["scrollup", "scrolldown"]:
            return

        if touch.button == "scrollup":
            projected_scale_factor = self.scale_factor / 1.2

        if touch.button == "scrolldown":
            projected_scale_factor = self.scale_factor * 1.2
        

        if projected_scale_factor >= 40:
            projected_scale_factor = 40

        if projected_scale_factor == 1000:
            return
        
        print('projected scale factor', projected_scale_factor)

        zoom_anim = Animation(scale_factor=projected_scale_factor, duration=0.15, transition='out_circ')

        projected_cursor_pos = self.point_to_pixel(
            cursor_coords_before_zoom, projected_scale_factor
        )

        pan_x = self.d_x + cursor_pos_before_zoom[0] - projected_cursor_pos[0]
        pan_y = self.d_y + cursor_pos_before_zoom[1] - projected_cursor_pos[1]

        zoom_anim &= Animation(d_x=pan_x, d_y=pan_y, duration=0.15, transition='out_circ')

        zoom_anim.start(self)


    def on_panning(self, touch_dx, touch_dy):
        self.d_x += touch_dx
        self.d_y += touch_dy


    def update_min_max(self):
        self.x_min = math.floor(
            (self.x - self.origin_x) / (self.major_tick_size * self.scale_factor)
        )
        self.x_max = math.ceil(
            (self.x + self.width - self.origin_x)
            / (self.major_tick_size * self.scale_factor)
        )

        self.y_min = math.floor(
            (self.y - self.origin_y) / (self.major_tick_size * self.scale_factor)
        )
        self.y_max = math.ceil(
            (self.y + self.height - self.origin_y)
            / (self.major_tick_size * self.scale_factor)
        )

        self.update_step()


    def update_step(self):
        step_gapx = self.x_max - self.x_min
        log_of_step = math.log10(step_gapx)
        base = 1
        power = math.floor(log_of_step)
        fractional_part = log_of_step - power

        if fractional_part <= self.unit_selection_diff:
            base = 1
        elif (
            self.unit_selection_diff <= fractional_part <= self.unit_selection_diff * 2
        ):
            base = 2
        else:
            base = 5

        self.unit_x = base * (10 ** (power - 1))
        self.unit_y = self.unit_x

        print(self.unit_x, log_of_step, power, base, fractional_part)

        self.unit_minor_x = self.unit_x / 5
        self.unit_minor_y = self.unit_minor_x
        self.precision = power


    def get_label(self, major_ticks, axis):

        axes_index = {'x': 0, 'y': 1}

        if axis not in axes_index:
            return
        
        index = axes_index[axis]
        
        for tick in major_ticks:
            label_pos = self.point_to_pixel(tick)
            
            if abs(tick[index]) <= 1e-10: 

                if axis == 'y':
                    continue  
                else:
                    label_pos = (label_pos[0] + 5, label_pos[1] + 5)
            else:
                if axis == 'x':
                    label_pos = (label_pos[0], label_pos[1] + 5)
                else:
                    label_pos = (label_pos[0] + 5, label_pos[1])

            if not tick[index].is_integer():
                p = (self.precision * -1) + 1

                label_txt = f'{tick[index]: .{p}f}'
                if label_txt == '-0.0':
                    label_txt = '0.0'

            else:
                label_txt = f'{int(tick[index])}'

            # c = ColorProperty(colormap='black')
            c = (0, 0, 0, 1)
            
            if axis == 'y':
                replace_label_pos = list(label_pos)

                if label_pos[0] <= self.x:
                    replace_label_pos[0] = self.x + 5
                    label_pos = tuple(replace_label_pos)
                    c = (0.33, 0.33, 0.33, 0.5)
                
                elif label_pos[0] >= self.x + self.width:
                    replace_label_pos[0] = self.x + self.width - 5
                    label_pos = tuple(label_pos)
                    c = (0.33, 0.33, 0.33, 0.5)
            
            
            if axis == 'x':
                replace_label_pos = list(label_pos)

                if label_pos[1] <= self.y:
                    replace_label_pos[1] = self.y + 5
                    label_pos = tuple(replace_label_pos)
                    c = (0.33, 0.33, 0.33, 0.5)

                elif label_pos[1] >= self.top:
                    replace_label_pos[1] = self.top - 5
                    label_pos = tuple(replace_label_pos)
                    c = (0.33, 0.33, 0.33, 0.5)
                

            label = CoreLabel(
                        text=label_txt, 
                        font_size=20,
                        color=c, 
                        font_name=self.font_path
                    )
            
            label.refresh()
            label_texture = label.texture
            self.label_widgets.add(Rectangle(pos=label_pos, texture=label_texture, size=label_texture.size))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_dir = Path(__file__).resolve().parents[2]
        self.font_path = str(self.root_dir / 'resources' / 'IosevkaTermNerdFont-Medium.ttf')

        self.scale_factor = 1

        self.update_event = Clock.create_trigger(self.update_plane)

        self.unit_selection_diff = 1 / 3

        self.unit_x = 1.0 / self.scale_factor
        self.unit_y = 1.0 / self.scale_factor

        self.unit_minor_x = self.unit_x / 5
        self.unit_minor_y = self.unit_minor_x

        self.vertical_grid_mesh = Mesh(mode="lines")
        self.horizontal_grid_mesh = Mesh(mode="lines")

        self.minor_vertical_grid_mesh = Mesh(mode="lines")
        self.minor_horizontal_grid_mesh = Mesh(mode="lines")

        self.x_axis = Line(width=1.5)
        self.y_axis = Line(width=1.5)

        self.major_tick_size = self.width / 10
        self.minor_tick_size = self.major_tick_size / 5

        self.canvas.add(Color(0, 0, 0, 1))
        self.canvas.add(self.vertical_grid_mesh)
        self.canvas.add(self.horizontal_grid_mesh)

        self.canvas.add(Color(0, 0, 0, 0.2))
        self.canvas.add(self.minor_vertical_grid_mesh)
        self.canvas.add(self.minor_horizontal_grid_mesh)

        # Invert color for black -> white
        self.canvas.add(Color(0, 0, 0, 1))
        self.canvas.add(self.x_axis)
        self.canvas.add(self.y_axis)

        self.canvas.add(self.label_widgets)

        self.bind(
            scale_factor=self.update_event, d_x=self.update_event, d_y=self.update_event
        )

        self.update_plane()

    # Tick generating functions: Basically create the visible major ticks on the screen using x_min as ref

    def get_major_x_ticks(self):
        major_x_ticks = []
        tick = math.ceil(self.x_min / self.unit_x) * self.unit_x

        while tick <= self.x_max:
            major_x_ticks.append([tick, 0])
            tick += self.unit_x

        return major_x_ticks
    

    def get_major_y_ticks(self):
        major_y_ticks = []
        tick = math.ceil(self.y_min / self.unit_y) * self.unit_y

        while tick <= self.y_max:
            major_y_ticks.append([0, tick])
            tick += self.unit_y

        return major_y_ticks
    

    def get_minor_x_ticks(self):
        minor_x_ticks = []
        tick = self.unit_x * (math.ceil(self.x_min / self.unit_x) - 1)

        while tick <= self.x_max + self.unit_x:
            minor_x_ticks.append([tick, 0])
            tick += self.unit_minor_x

        return minor_x_ticks
    

    def get_minor_y_ticks(self):
        minor_y_ticks = []
        tick = self.unit_y * (math.ceil(self.y_min / self.unit_y) - 1)
        while tick <= self.y_max + self.unit_x:
            minor_y_ticks.append([0, tick])
            tick += self.unit_minor_y

        return minor_y_ticks

    # Grid Drawing Functions: Draw the main grid on the screen using Meshes

    def init_vertical_grid(self, major_ticks):
        ver_vertices = []
        screen_top = self.y + self.height
        screen_bot = self.y

        for interval in major_ticks:
            if abs(interval[0]) < 1e-5:
                continue

            pixel_x = self.point_to_pixel(interval)[0]
            ver_vertices.extend([pixel_x, screen_top, 0, 0, pixel_x, screen_bot, 0, 0])

        total_vertices = len(ver_vertices) // 4

        self.vertical_grid_mesh.indices = list(range(total_vertices))
        self.vertical_grid_mesh.vertices = ver_vertices


    def init_horizontal_grid(self, major_ticks):
        hor_vertices = []
        screen_left = self.x
        screen_right = self.x + self.width

        for interval in major_ticks:
            if abs(interval[1]) < 1e-5:
                continue

            pixel_y = self.point_to_pixel(interval)[1]
            hor_vertices.extend(
                [screen_left, pixel_y, 0, 0, screen_right, pixel_y, 0, 0]
            )

        total_vertices = len(hor_vertices) // 4

        self.horizontal_grid_mesh.indices = list(range(total_vertices))
        self.horizontal_grid_mesh.vertices = hor_vertices


    def init_minor_vertical_grid(self, minor_ticks):
        minor_ver_vertices = []
        screen_top = self.y + self.height
        screen_bot = self.y

        for tick in minor_ticks:
            pixelx = self.point_to_pixel(tick)[0]
            minor_ver_vertices.extend(
                [pixelx, screen_top, 0, 0, pixelx, screen_bot, 0, 0]
            )

        total_vertices = len(minor_ver_vertices) // 4

        self.minor_vertical_grid_mesh.indices = list(range(total_vertices))
        self.minor_vertical_grid_mesh.vertices = minor_ver_vertices

    def init_minor_horizontal_grid(self, minor_ticks):
        minor_hor_vertices = []
        screen_left = self.x
        screen_right = self.x + self.width

        for tick in minor_ticks:
            pixely = self.point_to_pixel(tick)[1]
            minor_hor_vertices.extend(
                [screen_left, pixely, 0, 0, screen_right, pixely, 0, 0]
            )

        total_vertices = len(minor_hor_vertices) // 4
        self.minor_horizontal_grid_mesh.indices = list(range(total_vertices))
        self.minor_horizontal_grid_mesh.vertices = minor_hor_vertices


    def update_plane(self, *args):

        self.origin_x = self.get_origin_x()
        self.origin_y = self.get_origin_y()

        self.major_tick_size = self.width / 10  # Size of one major partition
        self.minor_tick_size = self.major_tick_size / 5

        self.update_min_max()

        major_x_ticks = self.get_major_x_ticks()
        major_y_ticks = self.get_major_y_ticks()

        minor_x_ticks = self.get_minor_x_ticks()
        minor_y_ticks = self.get_minor_y_ticks()

        self.x_axis.points = [self.x, self.origin_y, self.x + self.width, self.origin_y]
        self.y_axis.points = [self.origin_x, self.y, self.origin_x, self.top]

        self.init_vertical_grid(major_x_ticks)
        self.init_horizontal_grid(major_y_ticks)
        self.init_minor_vertical_grid(minor_x_ticks)
        self.init_minor_horizontal_grid(minor_y_ticks)

        self.label_widgets.clear()
        self.get_label(major_x_ticks, 'x')
        self.get_label(major_y_ticks, 'y')
        

    def on_size(self, *args):
        self.update_plane()
