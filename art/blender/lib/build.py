"""bmesh-сборка low-poly моделей с покраской граней в ячейки палитры."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import palette


def center(face) -> Vector:
    return face.calc_center_median()


def tri_count(obj) -> int:
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    # --- примитивы -----------------------------------------------------
    def sphere(self, segments, rings, scale, location, cell):
        m = Matrix.Translation(Vector(location)) @ Matrix.Diagonal((*scale, 1.0))
        r = bmesh.ops.create_uvsphere(self.bm, u_segments=segments, v_segments=rings, radius=1.0, matrix=m)
        return self._finish_part(r["verts"], cell)

    def cylinder(self, segments, radius, depth, location, cell, axis="Y"):
        rot = {"Z": Matrix.Identity(4), "Y": Matrix.Rotation(math.radians(90), 4, "X"),
               "X": Matrix.Rotation(math.radians(90), 4, "Y")}[axis]
        m = Matrix.Translation(Vector(location)) @ rot
        r = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segments,
                                  radius1=radius, radius2=radius, depth=depth, matrix=m)
        return self._finish_part(r["verts"], cell)

    def box(self, scale, location, cell):
        m = Matrix.Translation(Vector(location)) @ Matrix.Diagonal((*scale, 1.0))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=m)
        return self._finish_part(r["verts"], cell)

    # --- покраска -------------------------------------------------------
    def paint(self, faces, cell):
        u, v = palette.cell_uv(cell)
        index = 1 if palette.is_emissive(cell) else 0
        for f in faces:
            f.material_index = index
            for loop in f.loops:
                loop[self.uv].uv = (u, v)

    # --- завершение -------------------------------------------------------
    def finish(self, name, materials, smooth_angle_deg=30.0):
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        for mat in materials:
            mesh.materials.append(mat)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(smooth_angle_deg), keep_sharp_edges=False)
        return obj

    def _finish_part(self, verts, cell):
        vs = set(verts)
        faces = [f for f in self.bm.faces if all(v in vs for v in f.verts)]
        self.bm.normal_update()
        self.paint(faces, cell)
        return faces
