"""bmesh-сборка low-poly моделей с покраской граней в ячейки палитры.

Примитивы: `sphere`, `cylinder`, `box`, `lathe` (тело вращения вокруг локальной
оси Y). Правки формы: `deform` (произвольная функция по вершинам) и `bevel`
(фаска по рёбрам). Все примитивы красят свои грани сразу и возвращают список
граней, чтобы вызывающий код мог перекрасить часть из них по геометрии.

Модификаторы не используются: `finish` отдаёт готовый меш, экспорт ничего не
пересчитывает.
"""
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

    def lathe(self, profile, segments, location, cell, scale=(1.0, 1.0), cap=True, flip=False):
        """Тело вращения вокруг локальной оси Y.

        `profile` — точки (radius, y) от носа к корме (y убывает). Радиус 0 на
        конце даёт вершину-полюс и веер треугольников; радиус > 0 оставляет
        открытое кольцо, если `cap=False`, иначе закрывает его n-угольником.
        `scale=(sx, sz)` сжимает радиусы по X и Z независимо — сечение эллипс.
        `flip=True` разворачивает нормали внутрь: так строятся видимые изнутри
        поверхности (жерло сопла), потому что материалы палитры односторонние.
        """
        sx, sz = scale
        origin = Vector(location)
        step = 2.0 * math.pi / segments
        rings = []
        for radius, y in profile:
            if radius <= 0.0:
                rings.append([self.bm.verts.new(origin + Vector((0.0, y, 0.0)))])
                continue
            rings.append([
                self.bm.verts.new(origin + Vector((
                    radius * sx * math.cos(i * step), y, radius * sz * math.sin(i * step))))
                for i in range(segments)
            ])

        # Порядок обхода подобран так, чтобы нормали смотрели наружу без recalc.
        faces = []
        for top, bottom in zip(rings, rings[1:]):
            for i in range(segments):
                j = (i + 1) % segments
                if len(top) == 1:
                    loop = (top[0], bottom[j], bottom[i])
                elif len(bottom) == 1:
                    loop = (top[i], top[j], bottom[0])
                else:
                    loop = (top[i], top[j], bottom[j], bottom[i])
                faces.append(self.bm.faces.new(loop))
        if cap:
            if len(rings[0]) > 1:
                faces.append(self.bm.faces.new(tuple(reversed(rings[0]))))
            if len(rings[-1]) > 1:
                faces.append(self.bm.faces.new(tuple(rings[-1])))
        if flip:
            for f in faces:
                f.normal_flip()
        self.bm.normal_update()
        self.paint(faces, cell)
        return faces

    # --- правки формы ----------------------------------------------------
    def deform(self, faces, fn):
        """Двигает каждую уникальную вершину граней: `fn(Vector) -> Vector`."""
        for v in {v for f in faces if f.is_valid for v in f.verts}:
            v.co = Vector(fn(Vector(v.co)))
        self.bm.normal_update()
        return faces

    def bevel(self, faces, offset=0.03, segments=2, cell=None):
        """Фаска по всем рёбрам набора граней: коробки перестают быть картонными.

        Возвращает уцелевшие исходные грани вместе с новыми. `cell` красит
        результат целиком — у новых граней своей развёртки нет.
        """
        edges = list({e for f in faces if f.is_valid for e in f.edges})
        result = bmesh.ops.bevel(self.bm, geom=edges, offset=offset, segments=segments,
                                 affect="EDGES", profile=0.7)
        out = list(dict.fromkeys([f for f in faces if f.is_valid]
                                 + [f for f in result["faces"] if f.is_valid]))
        self.bm.normal_update()
        if cell is not None:
            self.paint(out, cell)
        return out

    # --- покраска -------------------------------------------------------
    def paint(self, faces, cell):
        u, v = palette.cell_uv(cell)
        index = 1 if palette.is_emissive(cell) else 0
        for f in faces:
            f.material_index = index
            for loop in f.loops:
                loop[self.uv].uv = (u, v)

    # --- завершение -------------------------------------------------------
    def finish(self, name, smooth_angle_deg=30.0):
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        # Порядок слотов фиксирован: 0 — базовый, 1 — эмиссивный (см. paint).
        try:
            slots = [bpy.data.materials["palette"], bpy.data.materials["palette_emit"]]
        except KeyError as exc:
            raise SystemExit("MATERIALS_MISSING: call ensure_palette_materials first") from exc
        for mat in slots:
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
