"""Blender (bpy) plates for reel 035: the gold cube in real 3D.
usage: bpyenv/bin/python gold3d.py <scene> <D seconds> <outdir> [--fps 30] [--pct 50] [--samples 12] [--still t1,t2] [--params json]
writes <outdir>/<scene>/NNNN.png (plate) and anchors.json (full-res 1080x1920 pixel coords of named 3D points per frame)."""
import bpy, bmesh, sys, os, json, math, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
SCENE, D, OUT = argv[0], float(argv[1]), argv[2]
def opt(name, default):
    return argv[argv.index(name) + 1] if name in argv else default
CAMK = float(opt("--camk", 0.3)); FPS = int(opt("--fps", 30)); PCT = int(opt("--pct", 50)); SAMPLES = int(opt("--samples", 12))
STILLS = [float(x) for x in opt("--still", "").split(",") if x]
P = json.loads(opt("--params", "{}"))
G = 22.64; RS = 14.15; W, H = 1080, 1920

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, k): return [a[i] + (b[i] - a[i]) * k for i in range(len(a))]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; cy = sc.cycles
cy.device = "CPU"; cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.04
cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 4; cy.diffuse_bounces = 1; cy.glossy_bounces = 3; cy.transmission_bounces = 0; cy.transparent_max_bounces = 2
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, PCT
sc.render.film_transparent = False
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = float(P.get("exposure", 0.0))
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"

# ---------- helpers
def mat(name, color, metal=0.0, rough=0.5, emit=None, estr=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = estr
    return m

def box(name, size, loc, m=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new("bev", "BEVEL"); bv.width = bevel; bv.segments = 3; bv.limit_method = "ANGLE"
    if m: o.data.materials.append(m)
    return o

def cyl(name, r, h, loc, m=None, verts=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts, rotation=rot); o = bpy.context.object; o.name = name
    if m: o.data.materials.append(m)
    return o

def bool_cut(target, cutter):
    md = target.modifiers.new("cut", "BOOLEAN"); md.object = cutter; md.operation = "DIFFERENCE"; md.solver = "EXACT"
    bpy.context.view_layer.objects.active = target; bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.object; o.name = name
    return o

def emitter(name, size, loc, rot, color, strength):
    """big soft panel seen only in reflections (camera can't see it)"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = name; o.scale = (*size, 1)
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (*color, 1); e.inputs[1].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], out.inputs[0]); o.data.materials.append(m)
    o.visible_camera = False; o.visible_shadow = False
    return o

def area(name, loc, target, size, power, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, "AREA"); l.size = size; l.energy = power; l.color = color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return o

def spot(name, loc, target, power, color, angle=40):
    l = bpy.data.lights.new(name, "SPOT"); l.energy = power; l.color = color; l.spot_size = math.radians(angle); l.spot_blend = 0.6
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return o

# ---------- world: camera sees a dark night gradient; reflections see a warm studio (Light Path trick)
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
def ramp_node(pairs):
    r = nt.nodes.new("ShaderNodeValToRGB"); el = r.color_ramp.elements
    el[0].position, el[0].color = pairs[0][0], (*pairs[0][1], 1); el[1].position, el[1].color = pairs[-1][0], (*pairs[-1][1], 1)
    for pos, col in pairs[1:-1]: e = el.new(pos); e.color = (*col, 1)
    return r
# Generated Z of world = direction z in [-1,1] mapped... use Normal-ish: Generated on world gives direction; Z -1..1
mz = nt.nodes.new("ShaderNodeMapRange"); mz.inputs[1].default_value = -1; mz.inputs[2].default_value = 1; nt.links.new(sep.outputs["Z"], mz.inputs[0])
cam_r = ramp_node([(0.0, (0.002, 0.002, 0.003)), (0.5, (0.003, 0.003, 0.004)), (0.56, (0.010, 0.007, 0.005)), (0.75, (0.004, 0.005, 0.010)), (1.0, (0.001, 0.002, 0.006))])
nt.links.new(mz.outputs[0], cam_r.inputs[0])
st = float(P.get("studio", 1.0))
ref_r = ramp_node([(0.0, (0.22, 0.14, 0.07)), (0.47, (0.45, 0.30, 0.16)), (0.52, (1.6 * st, 1.15 * st, 0.70 * st)), (0.60, (0.55 * st, 0.40 * st, 0.26 * st)), (0.80, (0.10 * st, 0.08 * st, 0.07 * st)), (1.0, (0.35 * st, 0.32 * st, 0.30 * st))])
nt.links.new(mz.outputs[0], ref_r.inputs[0])
# vertical "softbox strips" around the horizon for crisp streaks on the faces
sx_ = nt.nodes.new("ShaderNodeMath"); sx_.operation = "ARCTAN2"; nt.links.new(sep.outputs["Y"], sx_.inputs[0]); nt.links.new(sep.outputs["X"], sx_.inputs[1])
sn = nt.nodes.new("ShaderNodeMath"); sn.operation = "SINE"; mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 3.0
nt.links.new(sx_.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], sn.inputs[0])
pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 24.0; nt.links.new(sn.outputs[0], pw.inputs[0])
band = nt.nodes.new("ShaderNodeMapRange"); band.inputs[1].default_value = 0.48; band.inputs[2].default_value = 0.62; nt.links.new(mz.outputs[0], band.inputs[0])
bnd2 = nt.nodes.new("ShaderNodeMath"); bnd2.operation = "PINGPONG"; bnd2.inputs[1].default_value = 0.5; nt.links.new(band.outputs[0], bnd2.inputs[0])
strip = nt.nodes.new("ShaderNodeMath"); strip.operation = "MULTIPLY"; nt.links.new(pw.outputs[0], strip.inputs[0]); nt.links.new(bnd2.outputs[0], strip.inputs[1])
sadd = nt.nodes.new("ShaderNodeMix"); sadd.data_type = "RGBA"; sadd.blend_type = "ADD"; nt.links.new(strip.outputs[0], sadd.inputs["Factor"])
nt.links.new(ref_r.outputs[0], sadd.inputs[6]); sadd.inputs[7].default_value = (6.0 * st, 5.0 * st, 4.0 * st, 1)
lp = nt.nodes.new("ShaderNodeLightPath"); mixw = nt.nodes.new("ShaderNodeMix"); mixw.data_type = "RGBA"
nt.links.new(lp.outputs["Is Camera Ray"], mixw.inputs["Factor"]); nt.links.new(sadd.outputs[2], mixw.inputs[6]); nt.links.new(cam_r.outputs[0], mixw.inputs[7])
bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs[1].default_value = 1.0; nt.links.new(mixw.outputs[2], bg.inputs[0])
wo = nt.nodes.new("ShaderNodeOutputWorld"); nt.links.new(bg.outputs[0], wo.inputs[0])

# ---------- materials
def gold_mat(name="gold", tint=(1.0, 0.74, 0.30), rough=0.14):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Metallic"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[3].default_value = rough * 0.6; mr.inputs[4].default_value = rough * 1.5
    nt.links.new(nz.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs["Roughness"])
    # base colour: gold tint, with optional "before 1950" darkening below a height (driven by value node 'split')
    col = nt.nodes.new("ShaderNodeRGB"); col.outputs[0].default_value = (*tint, 1); col.name = "tint"
    old = nt.nodes.new("ShaderNodeRGB"); old.outputs[0].default_value = (0.55, 0.30, 0.09, 1); old.name = "old"
    sepz = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sepz.inputs[0])
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = -1e6; lt.name = "splitz"
    nt.links.new(sepz.outputs["Z"], lt.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; nt.links.new(lt.outputs[0], mix.inputs["Factor"])
    nt.links.new(col.outputs[0], mix.inputs[6]); nt.links.new(old.outputs[0], mix.inputs[7]); nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    # fine brushed bump
    nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 40; nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.04; nt.links.new(nz2.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

GOLD = gold_mat()
floor_m = bpy.data.materials.new("floor"); floor_m.use_nodes = True; fb = floor_m.node_tree.nodes["Principled BSDF"]
fb.inputs["Base Color"].default_value = (0.012, 0.012, 0.014, 1); fb.inputs["Roughness"].default_value = 0.22; fb.inputs["Specular IOR Level"].default_value = 0.35
fnt = floor_m.node_tree; ftc = fnt.nodes.new("ShaderNodeTexCoord"); fnz = fnt.nodes.new("ShaderNodeTexNoise"); fnz.inputs["Scale"].default_value = 0.08
fnt.links.new(ftc.outputs["Object"], fnz.inputs["Vector"]); fmr = fnt.nodes.new("ShaderNodeMapRange"); fmr.inputs[3].default_value = 0.28; fmr.inputs[4].default_value = 0.5
fnt.links.new(fnz.outputs["Fac"], fmr.inputs[0]); fnt.links.new(fmr.outputs[0], fb.inputs["Roughness"])
flw = fnt.nodes.new("ShaderNodeLayerWeight"); flw.inputs["Blend"].default_value = 0.5; fsm = fnt.nodes.new("ShaderNodeMapRange")
fsm.inputs[1].default_value = 0.35; fsm.inputs[2].default_value = 0.65; fsm.inputs[3].default_value = 0.5; fsm.inputs[4].default_value = 0.0
fnt.links.new(flw.outputs["Facing"], fsm.inputs[0]); fnt.links.new(fsm.outputs[0], fb.inputs["Specular IOR Level"])
# stone slab grid on floor (6 m tiles)
brk = fnt.nodes.new("ShaderNodeTexBrick"); brk.offset = 0.0; brk.inputs["Scale"].default_value = 1 / 6.0; brk.inputs["Mortar Size"].default_value = 0.012
brk.inputs["Color1"].default_value = (1, 1, 1, 1); brk.inputs["Color2"].default_value = (1, 1, 1, 1); brk.inputs["Mortar"].default_value = (0, 0, 0, 1)
brk.inputs["Brick Width"].default_value = 1.0; brk.inputs["Row Height"].default_value = 1.0
fnt.links.new(ftc.outputs["Object"], brk.inputs["Vector"]); fbp = fnt.nodes.new("ShaderNodeBump"); fbp.inputs["Strength"].default_value = 0.25
fnt.links.new(brk.outputs["Fac"], fbp.inputs["Height"]); fnt.links.new(fbp.outputs["Normal"], fb.inputs["Normal"])

def glossy_warm(m, col=(0.42, 0.26, 0.11), strength=1.0):
    nt_ = m.node_tree; outn = [n for n in nt_.nodes if n.type == "OUTPUT_MATERIAL"][0]; src = outn.inputs["Surface"].links[0].from_socket
    lp_ = nt_.nodes.new("ShaderNodeLightPath"); em_ = nt_.nodes.new("ShaderNodeEmission"); em_.inputs[0].default_value = (*col, 1); em_.inputs[1].default_value = strength
    mx_ = nt_.nodes.new("ShaderNodeMixShader"); nt_.links.new(lp_.outputs["Is Glossy Ray"], mx_.inputs[0])
    nt_.links.new(src, mx_.inputs[1]); nt_.links.new(em_.outputs[0], mx_.inputs[2]); nt_.links.new(mx_.outputs[0], outn.inputs["Surface"])
glossy_warm(floor_m, (0.34, 0.22, 0.08), float(P.get("floorglow", 0.8)))

SAND = bpy.data.materials.new("sand"); SAND.use_nodes = True; snt = SAND.node_tree; sb = snt.nodes["Principled BSDF"]
stc = snt.nodes.new("ShaderNodeTexCoord"); snz = snt.nodes.new("ShaderNodeTexNoise"); snz.inputs["Scale"].default_value = 1.2; snz.inputs["Detail"].default_value = 8
snt.links.new(stc.outputs["Object"], snz.inputs["Vector"]); sr = snt.nodes.new("ShaderNodeValToRGB")
sr.color_ramp.elements[0].color = (0.36, 0.17, 0.07, 1); sr.color_ramp.elements[1].color = (0.55, 0.33, 0.16, 1)
snt.links.new(snz.outputs["Fac"], sr.inputs[0]); snt.links.new(sr.outputs[0], sb.inputs["Base Color"]); sb.inputs["Roughness"].default_value = 0.85
sbp = snt.nodes.new("ShaderNodeBump"); sbp.inputs["Strength"].default_value = 0.3; snt.links.new(snz.outputs["Fac"], sbp.inputs["Height"]); snt.links.new(sbp.outputs["Normal"], sb.inputs["Normal"])

PERSON = mat("person", (0.55, 0.58, 0.62), 0.0, 0.6)
PERSON_D = mat("person_d", (0.05, 0.06, 0.08), 0.0, 0.6)

# ---------- objects
def gold_cube(name, side, loc=(0, 0, 0), m=GOLD):
    o = box(name, (side, side, side), (loc[0], loc[1], loc[2] + side / 2), m, bevel=side * 0.006)
    o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))
    return o

def person(name, x, y, z=0.0, rot=0.0, h=1.75, m=None):
    s = h / 1.75; parts = []
    parts.append(cyl(name + "_l1", 0.075 * s, 0.85 * s, (x - 0.1 * s, y, z + 0.425 * s), verts=10))
    parts.append(cyl(name + "_l2", 0.075 * s, 0.85 * s, (x + 0.1 * s, y, z + 0.425 * s), verts=10))
    parts.append(cyl(name + "_t", 0.19 * s, 0.62 * s, (x, y, z + 1.16 * s), verts=12))
    parts.append(cyl(name + "_a1", 0.055 * s, 0.6 * s, (x - 0.26 * s, y, z + 1.12 * s), verts=8))
    parts.append(cyl(name + "_a2", 0.055 * s, 0.6 * s, (x + 0.26 * s, y, z + 1.12 * s), verts=8))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12 * s, location=(x, y, z + 1.62 * s), segments=12, ring_count=8); parts.append(bpy.context.object)
    o = join(parts, name); o.data.materials.clear(); o.data.materials.append(m or PERSON); o.rotation_euler[2] = rot
    return o

def india_gate(x, y, rot=0.0):
    """India Gate, simplified massing; total height 42 m (DM New Delhi / Delhi Tourism)."""
    parts = []
    parts.append(box("ig_plinth", (31, 14, 1.4), (0, 0, 0.7)))
    body = box("ig_body", (25, 9.5, 27.5), (0, 0, 1.4 + 13.75))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.4 + 7.25)); c1 = bpy.context.object; c1.scale = (9.1, 14, 14.5); bpy.ops.object.transform_apply(scale=True)
    bool_cut(body, c1); c2 = cyl("ig_c2", 4.55, 14, (0, 0, 1.4 + 14.5), rot=(math.pi / 2, 0, 0), verts=48); bool_cut(body, c2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.4 + 4.5)); c3 = bpy.context.object; c3.scale = (30, 4.2, 9); bpy.ops.object.transform_apply(scale=True)
    bool_cut(body, c3); c4 = cyl("ig_c4", 2.1, 30, (0, 0, 1.4 + 9.0), rot=(0, math.pi / 2, 0), verts=32); bool_cut(body, c4)
    for sx in (-1, 1):   # recessed panels on the piers
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx * 8.6, -4.85, 1.4 + 16)); cp = bpy.context.object; cp.scale = (3.2, 0.5, 12); bpy.ops.object.transform_apply(scale=True); bool_cut(body, cp)
    parts.append(body)
    parts.append(box("ig_band", (26.2, 10.6, 1.0), (0, 0, 1.4 + 21.5)))
    parts.append(box("ig_corn", (26.6, 11.0, 1.4), (0, 0, 1.4 + 27.5 + 0.7)))
    parts.append(box("ig_att1", (21, 8.2, 5.2), (0, 0, 30.3 + 2.6)))
    parts.append(box("ig_att1c", (21.8, 9.0, 0.7), (0, 0, 35.5 + 0.35)))
    parts.append(box("ig_att2", (15.5, 6.6, 3.0), (0, 0, 36.2 + 1.5)))
    parts.append(box("ig_att3", (10.5, 5.2, 2.2), (0, 0, 39.2 + 1.1)))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.0, location=(0, 0, 41.4), segments=32, ring_count=16); dome = bpy.context.object
    dome.scale = (1, 1, 0.2); bpy.ops.object.transform_apply(scale=True); parts.append(dome)
    o = join(parts, "india_gate"); o.data.materials.clear(); o.data.materials.append(SAND)
    o.location = (x, y, 0); o.rotation_euler[2] = rot
    return o

bpy.ops.mesh.primitive_plane_add(size=20000, location=(0, 0, 0)); FLOOR = bpy.context.object; FLOOR.data.materials.append(floor_m)

# reflection softboxes + key lights (shared by every scene)
# emitter("soft_top", (60, 14), (0, -10, 70), (0.25, 0, 0), (1.0, 0.95, 0.88), 3.0)
# emitter("soft_left", (12, 50), (-70, -30, 30), (0, math.radians(-70), math.radians(20)), (1.0, 0.92, 0.80), 2.2)
# emitter("soft_right", (10, 40), (75, 10, 28), (0, math.radians(75), math.radians(-15)), (0.75, 0.85, 1.0), 1.4)
area("key", (-45, -60, 55), (0, 0, 10), 12, float(P.get("key", 30000)), (1.0, 0.88, 0.72))
area("rim", (40, 60, 30), (0, 0, 12), 20, 25000, (0.6, 0.75, 1.0))

cam_d = bpy.data.cameras.new("cam"); CAM = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(CAM); sc.camera = CAM
cam_d.lens = 30; cam_d.sensor_fit = "VERTICAL"; cam_d.sensor_height = 36; cam_d.clip_end = 3000

def set_cam(pos, target, lens=None):
    CAM.location = pos; d = Vector(target) - Vector(pos); CAM.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if lens: cam_d.lens = lens
    bpy.context.view_layer.update()

def orbit(target, dist, yaw, pitch):
    y, p = math.radians(yaw), math.radians(pitch)
    return [target[0] + dist * math.cos(p) * math.sin(y), target[1] - dist * math.cos(p) * math.cos(y), target[2] + dist * math.sin(p)]

ANCH = {}
def proj(name, p):
    v = world_to_camera_view(sc, CAM, Vector(p)); ANCH[name] = [round(v.x * W, 1), round((1 - v.y) * H, 1), round(v.z, 2)]

# ---------- scenes: build() once, then state(t) per frame
CUBE = gold_cube("cube", G)

def glow_ring():
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.02)); o = bpy.context.object; o.scale = (G + 6, G + 6, 1)
    m = bpy.data.materials.new("ring"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    tc = nt.nodes.new("ShaderNodeTexCoord"); gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    mpn = nt.nodes.new("ShaderNodeMapping"); mpn.inputs["Scale"].default_value = (1.0, 1.0, 1); nt.links.new(tc.outputs["Object"], mpn.inputs[0])
    nt.links.new(mpn.outputs[0], gr.inputs[0]); rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0, 0, 0, 1)
    rp.color_ramp.elements[1].position = 0.5; rp.color_ramp.elements[1].color = (1, 1, 1, 1); nt.links.new(gr.outputs[0], rp.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (1.0, 0.45, 0.08, 1); em.name = "em"; em.inputs[1].default_value = 0.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(rp.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(mx.outputs[0], out.inputs[0]); o.data.materials.append(m)
    return o, em

def split_set(m, z):
    m.node_tree.nodes["splitz"].inputs[1].default_value = z

if SCENE == "hook":
    for i, (px, py) in enumerate([(14, -16), (15.5, -14.5), (-13, -15.5)]): person(f"p{i}", px, py, rot=0.4 * i)
    def state(t):
        h = ease((t + 0.6) / 3.2); CUBE.location.z = -G * (1 - h)
        set_cam(orbit((0, 0, 9.5), 64 - 4 * CAMK, -38 + 14 * CAMK, 13), (0, 0, 9.5))

elif SCENE == "size":
    GX, GY = -40.0, 6.0
    GATE = india_gate(GX, GY, 0.0)
    spot("g1", (GX, GY - 30, 0.5), (GX, GY, 22), 2.2e5, (1.0, 0.62, 0.32), 45)
    spot("g2", (GX - 22, GY - 14, 0.5), (GX, GY, 20), 0.8e5, (1.0, 0.6, 0.3), 45)
    spot("g3", (GX + 20, GY - 14, 0.5), (GX, GY, 20), 0.8e5, (1.0, 0.6, 0.3), 45)
    ppl = [(9.5, -14.2, 0.3), (11.0, -13.4, 2.4), (8.4, -15.6, 1.0), (-2, -14.5, 0.0), (-0.8, -15.2, 2.6), (14.5, -12.5, 1.7)]
    for i, (px, py, r) in enumerate(ppl): person(f"p{i}", px, py, rot=r)
    ga = P.get("gate_at", 8.5)
    def state(t):
        if t < ga:
            tgt = [3, -4, 10]; set_cam(orbit(tgt, 52, -30, 7), tgt)
        else:
            tgt = [-19, 0, 19]; set_cam(orbit(tgt, 126, -4, 4), tgt)
        proj("cube_dim_b", (G / 2 + 1.5, -G / 2, 0)); proj("cube_dim_t", (G / 2 + 1.5, -G / 2, G))
        proj("gate_dim_b", (GX - 15.5, GY - 7, 0)); proj("gate_dim_t", (GX - 15.5, GY - 7, 42)); proj("gate_top", (GX, GY, 44.5))
        proj("person", (-2, -14.5, 1.9)); proj("cube_top", (0, 0, G + 2.5))

elif SCENE == "pitch":
    # cricket ground: grass, 22-yard pitch (20.12 m between the stumps, MCC Law 6.1), creases, stumps
    grass = bpy.data.materials.new("grass"); grass.use_nodes = True; gnt = grass.node_tree; gb = gnt.nodes["Principled BSDF"]
    gtc = gnt.nodes.new("ShaderNodeTexCoord"); wv = gnt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Y"; wv.inputs["Scale"].default_value = 0.025; wv.wave_profile = "SAW"
    gnt.links.new(gtc.outputs["Object"], wv.inputs["Vector"]); grr = gnt.nodes.new("ShaderNodeValToRGB")
    grr.color_ramp.interpolation = "CONSTANT"; grr.color_ramp.elements[0].color = (0.012, 0.045, 0.010, 1); grr.color_ramp.elements[1].position = 0.5; grr.color_ramp.elements[1].color = (0.020, 0.065, 0.016, 1)
    gnt.links.new(wv.outputs["Fac"], grr.inputs[0]); gnt.links.new(grr.outputs[0], gb.inputs["Base Color"]); gb.inputs["Roughness"].default_value = 0.95
    glossy_warm(grass, (0.30, 0.21, 0.08), 0.9)
    FLOOR.data.materials.clear(); FLOOR.data.materials.append(grass)
    PY = -G / 2 - 4.0   # pitch runs along x, right in front of the cube's front face (parallel to it)
    clay = mat("clay", (0.30, 0.20, 0.11), 0.0, 0.85); white = mat("white", (0.85, 0.85, 0.85), 0.0, 0.6)
    box("pitch", (20.12 + 2 * 1.6, 3.05, 0.03), (0, PY, 0.015), clay)
    wood = mat("wood", (0.80, 0.70, 0.50), 0.0, 0.5)
    for sx in (-1, 1):
        xb = sx * 20.12 / 2
        box(f"bc{sx}", (0.05, 2.64, 0.035), (xb, PY, 0.02), white)
        box(f"pc{sx}", (0.05, 3.66, 0.035), (xb - sx * 1.22, PY, 0.02), white)
        for sy in (-1, 1): box(f"rc{sx}{sy}", (2.44, 0.05, 0.035), (xb, PY + sy * 1.32, 0.02), white)
        for k in (-1, 0, 1): cyl(f"st{sx}{k}", 0.019, 0.711, (xb, PY + k * 0.1, 0.3555), wood, 10)
        box(f"bail{sx}", (0.025, 0.23, 0.025), (xb, PY, 0.725), wood)
    PX = 0.0
    for i, (fx, fy) in enumerate([(-120, 150), (150, 160), (-130, -150), (160, -140)]):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(fx, fy, 50)); o = bpy.context.object; o.scale = (12, 5, 1)
        d = Vector((0, 0, 0)) - o.location; o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        lm = bpy.data.materials.new(f"fl{i}"); lm.use_nodes = True; lnt = lm.node_tree; lnt.nodes.clear(); le = lnt.nodes.new("ShaderNodeEmission")
        le.inputs[0].default_value = (1, 0.97, 0.9, 1); le.inputs[1].default_value = 40; lo = lnt.nodes.new("ShaderNodeOutputMaterial"); lnt.links.new(le.outputs[0], lo.inputs[0]); o.data.materials.append(lm)
        cyl(f"tw{i}", 0.6, 50, (fx, fy, 25), mat(f"twm{i}", (0.1, 0.1, 0.1), 0.5, 0.5), 8)
        sun_ = bpy.data.lights.new(f"fs{i}", "SPOT"); sun_.energy = float(P.get("flood", 3.5e5)); sun_.spot_size = math.radians(70); sun_.spot_blend = 1.0
        so = bpy.data.objects.new(f"fs{i}", sun_); sc.collection.objects.link(so); so.location = (fx * 0.5, fy * 0.5, 45)
        so.rotation_euler = (Vector((PX - 4, 0, 0)) - so.location).to_track_quat("-Z", "Y").to_euler()
    person("bat", 20.12 / 2 - 1.5, PY + 0.3, rot=1.57, m=PERSON); person("keeper", 20.12 / 2 + 2.4, PY + 0.2, rot=1.57, m=PERSON); person("bowler", -20.12 / 2 - 1.0, PY - 0.6, rot=-1.57, m=PERSON)
    def state(t):
        k = CAMK
        tgt = [0, PY + 2, 7.5]; pos = [0, PY - 40, 24]
        set_cam(pos, tgt)
        proj("pitch_a", (-20.12 / 2, PY - 2.2, 0.0)); proj("pitch_b", (20.12 / 2, PY - 2.2, 0.0)); proj("pitch_mid", (0, PY - 2.4, 0.0))
        proj("cube_a", (-G / 2, -G / 2, G)); proj("cube_b", (G / 2, -G / 2, G)); proj("cube_bl", (-G / 2, -G / 2, 0)); proj("cube_br", (G / 2, -G / 2, 0))

elif SCENE == "1950":
    hb = G / 3
    def state(t):
        s = ease((t - 0.5) / 1.2)
        split_set(GOLD, hb if s > 0 else -1e6)
        GOLD.node_tree.nodes["old"].outputs[0].default_value = (*lerp([1.0, 0.60, 0.16], [0.42, 0.20, 0.05], s), 1)
        k = CAMK; set_cam(orbit((0, 0, 10), 64, 18 - 26 * k, 11), (0, 0, 10))
        proj("before", (G / 2 + 1.5, -G / 2, hb / 2))
        for nm_, pt_ in {"bl": (-G / 2, -G / 2, 0), "bm": (G / 2, -G / 2, 0), "br": (G / 2, G / 2, 0), "sl": (-G / 2, -G / 2, hb), "sm": (G / 2, -G / 2, hb), "sr": (G / 2, G / 2, hb)}.items(): proj(nm_, pt_)
        proj("after", (G / 2 + 1.5, -G / 2, hb + (G - hb) / 2)); proj("seam", (G / 2, -G / 2, hb))

elif SCENE == "grow":
    SLAB = gold_cube("slab", 1.0); SLAB.scale = (G, G, 0.37); SLAB.location = (0, 0, -50)
    SM = gold_mat("slabm", (1.0, 0.82, 0.42), 0.08); SLAB.data.materials.clear(); SLAB.data.materials.append(SM)
    sb_ = SM.node_tree.nodes["Principled BSDF"]; sb_.inputs["Emission Color"].default_value = (1.0, 0.55, 0.15, 1)
    TOPP = person("top", -G / 2 + 2.2, -G / 2 + 2.0, G, 0.5); TOPP2 = person("top2", -G / 2 + 3.3, -G / 2 + 2.6, G, 2.6)
    sa = P.get("slab_at", 6.0)
    def state(t):
        q = ease((t - sa) / 1.0) if t > sa else 0.0
        SLAB.location = (0, 0, (G + 6 * (1 - q)) if t > sa else -50)
        sb_.inputs["Emission Strength"].default_value = 2.5 * (1 - ease((t - sa - 1.0) / 2.0)) if t > sa else 0.0
        lift = 0.37 if q >= 1 else 0.0; TOPP.location.z = lift; TOPP2.location.z = lift
        k = CAMK; tgt = [-G / 2 + 6, -G / 2 + 6, G - 2.0]
        set_cam(orbit(tgt, 27, -38, 18), tgt)
        z0 = G + lift
        proj("person_top", (-G / 2 + 2.2, -G / 2 + 2.0, z0 + 1.9)); proj("person_feet", (-G / 2 + 2.2, -G / 2 + 2.0, z0))
        proj("slab_b", (-G / 2, -G / 2, G)); proj("slab_t", (-G / 2, -G / 2, G + 0.37))

elif SCENE == "reserve":
    RM = gold_mat("res", (0.85, 0.50, 0.14), 0.32); RC = gold_cube("rcube", RS, (0, 0, 0), RM); RC.location = (27, 6, -RS - 1)
    ra = P.get("res_at", 4.4)
    def state(t):
        q = ease((t - ra) / 1.4); RC.location = (27, 6 - RS / 2 + RS / 2, -RS * (1 - q) - (0.5 if q <= 0 else 0))
        RC.location.y = 6.0
        k = CAMK; tgt = [12, 3, 10]; set_cam(orbit(tgt, 84, -16 + 22 * k, 10), tgt)
        proj("res_top", (27, 6, RS + 2.5)); proj("big_top", (0, 0, G + 2.5))

elif SCENE == "end":
    for i, (px, py) in enumerate([(13.5, -14.0), (15.0, -13.2), (-6, -14.5)]): person(f"p{i}", px, py, rot=0.5 * i)
    def state(t):
        k = CAMK; set_cam(orbit((0, 0, 13), 82, -28 + 12 * k, 8), (0, 0, 13))

# move the RGB-node based split back off for scenes that never call split_set
os.makedirs(os.path.join(OUT, SCENE), exist_ok=True)
RNG = [float(x) for x in opt("--range", "").split(",") if x]
frames = [round(s * FPS) for s in STILLS] if STILLS else (list(range(round(RNG[0] * FPS), round(RNG[1] * FPS) + 1)) if RNG else list(range(int(math.ceil(D * FPS)))))
anchors = {}
t0 = time.time()
for n, f in enumerate(frames):
    t = f / FPS; ANCH.clear(); state(t)
    path = os.path.join(OUT, SCENE, f"{f:04d}.png")
    if "--anchors" not in argv and (STILLS or not os.path.exists(path)):
        sc.render.filepath = path; bpy.ops.render.render(write_still=True)
    anchors[f] = dict(ANCH)
    if n % 10 == 0: print(f"{SCENE} frame {f} ({n + 1}/{len(frames)}) {time.time() - t0:.0f}s", flush=True)
ap = os.path.join(OUT, SCENE, "anchors.json")
old = json.load(open(ap)) if os.path.exists(ap) else {}
old.update({str(k): v for k, v in anchors.items()}); json.dump(old, open(ap, "w"))
print("done", SCENE, len(frames), f"{time.time() - t0:.0f}s")
