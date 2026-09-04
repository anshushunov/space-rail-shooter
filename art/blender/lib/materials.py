"""Два материала на одну палитру: базовый и эмиссивный."""
import bpy


def ensure_palette_materials(palette_path: str):
    img = bpy.data.images.get("palette")
    if img is None:
        img = bpy.data.images.load(palette_path)
        img.name = "palette"
    img.colorspace_settings.name = "sRGB"
    return _make("palette", img, emissive=False), _make("palette_emit", img, emissive=True)


def _make(name: str, img, emissive: bool):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    bsdf.inputs["Roughness"].default_value = 0.6
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if emissive:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 3.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat
