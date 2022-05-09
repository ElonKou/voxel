
import taichi as ti
from scene import Scene
from taichi.math import *

scene = Scene(voxel_edges=0, exposure=10)
scene.set_background_color((0.12, 0.12, 0.12))
scene.set_floor(0.0, (1.0, 1.0, 1.0))
noise = vec3(0.05)

@ti.func
def create_block(pos, size, color, color_noise, tp):
    for I in ti.grouped(
            ti.ndrange((pos[0], pos[0] + size[0]), (pos[1], pos[1] + size[1]), (pos[2], pos[2] + size[2]))):
        scene.set_voxel(I, tp, color + color_noise * ti.random())

@ti.func
def create_strap(pos, dir, item, col, cnt):
    for i in range(cnt):
        num = i % 2
        create_block(pos + dir * i, item, col, noise * (1 - num), num + 1)

@ti.func
def create_building(start, sizes, cols, height, offset=True):
    cnt = sizes[0][1] + sizes[1][1]
    out = int((height + 1) / 2)
    for i in range(out):
        pos = start + ivec3(0, cnt * i, 0)
        create_block(pos, sizes[0], cols[0], noise, 1)
    for i in range(height - out):
        pos = start + ivec3(0, cnt * i + sizes[0][1], 0)
        if offset:
            pos = pos + ivec3(1, 0, 1)
        create_block(pos, sizes[1], cols[1], noise, 2)

@ti.func
def create_combined_building_1(pos, width, height, layer, cols, tp):
    _size = ivec3(width, 2, height)
    create_building(pos + ivec3(0, 0, 0), [_size, _size - ivec3(2, 1, 2)], cols, layer)
    _size = ivec3(height, 2, width)
    if tp > 1:
        create_building(pos + ivec3(width, 0, 2), [_size, _size - ivec3(2, 1, 2)], cols, layer)
    _size = ivec3(width, 2, height)
    if tp > 2:
        create_building(pos + ivec3(width + height, 0, 0), [_size, _size - ivec3(2, 1, 2)], cols, layer)

@ti.func
def create_building_2(pos, width, height, layer, cols):
    _size = ivec3(width, 2, height)
    cnt = int(1.5 * layer)
    create_building(pos + ivec3(0, 0, 0), [_size, _size - ivec3(2, 1, 2)], cols, layer)
    create_block(pos, ivec3(1, cnt, 1), cols[0], vec3(0), 1)
    create_block(pos + ivec3(width - 1, 0, height - 1), ivec3(1, cnt, 1), cols[0], vec3(0), 1)
    create_block(pos + ivec3(width - 1, 0, 0), ivec3(1, cnt, 1), cols[0], vec3(0), 1)
    create_block(pos + ivec3(0, 0, height - 1), ivec3(1, cnt, 1), cols[0], vec3(0), 1)

@ti.func
def create_building_3(pos, width, height, layer, cols):
    _size = ivec3(width, 2, height)
    cnt = int(1.5 * layer)
    create_building(pos + ivec3(0, 0, 0), [_size, _size - ivec3(2, 1, 2)], cols, layer)
    create_block(pos + ivec3(width // 2, 0, 0), ivec3(width // 2, layer // 2, height), cols[0], vec3(0), 0) # clear
    create_block(pos, ivec3(2, cnt, 2), cols[0], vec3(0), 1) 
    create_block(pos + ivec3(width - 3, 0, height - 3), ivec3(2, cnt, 2), cols[0], vec3(0), 1)
    create_block(pos + ivec3(width - 3, 0, 0), ivec3(2, cnt, 2), cols[0], vec3(0), 1)
    create_block(pos + ivec3(0, 0, height - 3), ivec3(2, cnt, 2), cols[0], vec3(0), 1)

@ti.func
def create_board(pos, width, height, layer, col):
    no = vec3(0.01)
    col = col * 0.15
    create_block(pos, ivec3(1, layer, 1), col, no, 2)
    create_block(pos + ivec3(width - 3, 0, 0), ivec3(1, layer, 1), col, no, 2)
    create_block(pos + ivec3(-1, layer, 0), ivec3(width, height, 1), col, no, 2)
    create_block(pos + ivec3(0, layer + 1, 0), ivec3(width - 2, height-2, 1), col*2, no, 2)

@ti.func
def create_light(pos, col, height):
    create_block(pos, ivec3(2, height, 2), col, noise, 1)
    create_block(pos + ivec3(2, height, 2) - ivec3(3, 0, 3),vec3(4, 4, 4), col, noise, 2)

@ti.kernel
def init_scene():
    create_strap(ivec3(-4, 0, 0), ivec3(0, 1, 0),ivec3(18, 1, 12), vec3(0.0, 0.6, 0.3), 19)
    create_strap(ivec3(-26, 0, 16), ivec3(0, 1, 0),ivec3(22, 1, 12), vec3(0.2, 0.0, 0.5), 11)
    create_strap(ivec3(-26, 0, 28), ivec3(0, 1, 0),ivec3(18, 1, 8), vec3(0.2, 0.0, 0.5), 5)
    create_strap(ivec3(20, 0, -16), ivec3(0, 2, 0),ivec3(16, 1, 24), vec3(0.8, 0.3, 0.1), 23)
    create_strap(ivec3(-40, 0, -32), ivec3(0, 2, 0),ivec3(20, 1, 32), vec3(0.92, 0.34, 0.2), 31)
    create_building(ivec3(30, 0, 20), [ivec3(20, 2, 30), ivec3(18, 1, 28)], [vec3(0.1, 0.4, 0.4), vec3(0.1, 0.4, 0.4)], 11)
    create_combined_building_1(ivec3(-30, 0, -64), 12, 20, 15, [vec3(0.12, 0.13, 0.4), vec3(0.1, 0.4, 0.4)], 3)
    create_light(ivec3(20, 0, 20), vec3(0.2, 0.7, 0.7), 5)
    create_light(ivec3(-20, 0, 15), vec3(0.9, 0.8, 0.2), 5)
    create_building_2(ivec3(40, 0, -20), 32, 30, 15, [vec3(0.8, 0.2, 0.4), vec3(0.7, 0.1, 0.6)])
    create_building_3(ivec3(-54, 0, 40), 22, 14, 11, [vec3(0.2, 0.4, 0.56), vec3(0.2, 0.1, 0.6)])
    create_board(ivec3(5, 0, 24), 12, 8, 3, vec3(0.8, 0.3, 0.1))
    create_board(ivec3(45, 23, -2), 14, 8, 3, vec3(0.1, 0.7, 0.8))

init_scene()
scene.finish()