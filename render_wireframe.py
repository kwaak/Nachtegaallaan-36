#!/usr/bin/env python3
"""Render the room wireframe (same scene as room-wireframe.html) to a PNG.
Pure stdlib: math, struct, zlib. No external dependencies."""
import math, struct, zlib

# ---- Room dimensions (meters), mirroring room-wireframe.html ----
W, L, H = 4.0, 8.5, 2.6   # width(X), length(Z), height(Y)

COL = {
    'shell':  (0x66, 0xcc, 0xff),
    'glass':  (0xff, 0xd2, 0x4a),
    'hearth': (0xff, 0x7a, 0x59),
    'closet': (0x9a, 0xf2, 0x8a),
    'sofa':   (0xc0, 0x8c, 0xff),
    'table':  (0xf5, 0xf5, 0xf5),
    'door':   (0xff, 0x5e, 0xa8),
    'grid':   (0x1f, 0x35, 0x4a),
    'axisx':  (0xff, 0x55, 0x55),
    'axisy':  (0x55, 0xff, 0x55),
    'axisz':  (0x55, 0x77, 0xff),
}

edges = []  # (p0, p1, color)

def add_edge(a, b, c):
    edges.append((a, b, c))

def box(w, h, d, cx, cy, cz, c):
    x0, x1 = cx - w/2, cx + w/2
    y0, y1 = cy - h/2, cy + h/2
    z0, z1 = cz - d/2, cz + d/2
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    E = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    for i,j in E: add_edge(v[i], v[j], c)

def rect(w, h, cx, cy, cz, c, axis='z'):
    # rectangle in plane; axis='z' -> spans X,Y ; axis='x' -> spans Z,Y
    if axis == 'z':
        v = [(cx-w/2,cy-h/2,cz),(cx+w/2,cy-h/2,cz),(cx+w/2,cy+h/2,cz),(cx-w/2,cy+h/2,cz)]
    else:
        v = [(cx,cy-h/2,cz-w/2),(cx,cy-h/2,cz+w/2),(cx,cy+h/2,cz+w/2),(cx,cy+h/2,cz-w/2)]
    for i in range(4): add_edge(v[i], v[(i+1)%4], c)

# --- Shell ---
box(W, H, L, 0, H/2, 0, COL['shell'])

# --- Floor grid ---
n = 16
for i in range(n+1):
    x = -W/2 + W*i/n
    add_edge((x,0,-L/2),(x,0,L/2), COL['grid'])
    z = -L/2 + L*i/n
    add_edge((-W/2,0,z),(W/2,0,z), COL['grid'])

# --- Garden glass wall (back, Z=-L/2) ---
backZ = -L/2
rect(W*0.85, H*0.78, 0, H*0.45, backZ+0.01, COL['glass'], 'z')
for fx in (-1/3, 1/3):
    rect(0.02, H*0.78, W*0.85*fx, H*0.45, backZ+0.02, COL['glass'], 'z')

# --- Fireplace (left wall X=-W/2) ---
leftX = -W/2
box(0.9, 1.4, 1.6, leftX+0.45, 0.7, L*0.18, COL['hearth'])
box(0.7, 0.55, 0.4, leftX+0.35, 0.42, L*0.18, COL['hearth'])

# --- Tall closet (right wall, near garden) ---
rightX = W/2
box(0.6, 2.2, 1.0, rightX-0.3, 1.1, -L*0.28, COL['closet'])

# --- Dining table + chairs ---
tableZ = -L*0.12
box(1.6, 0.04, 0.95, 0, 0.76, tableZ, COL['table'])
for sx in (-0.7, 0.7):
    for sz in (-0.4, 0.4):
        box(0.06, 0.74, 0.06, sx, 0.37, tableZ+sz, COL['table'])
for cx, cz in [(0,-0.7),(0,0.7),(-0.95,0),(0.95,0)]:
    box(0.45, 0.04, 0.45, cx, 0.46, tableZ+cz, COL['table'])
    box(0.45, 0.5, 0.05, cx, 0.7, tableZ+cz+(0.2 if cz>=0 else -0.2), COL['table'])

# --- Sofa + coffee table ---
box(0.9, 0.8, 2.2, rightX-0.45, 0.4, L*0.28, COL['sofa'])
box(1.1, 0.4, 0.6, W*0.05, 0.2, L*0.28, COL['sofa'])

# --- Doors ---
frontZ = L/2
rect(0.9, 2.1, W*0.25, 1.05, frontZ-0.01, COL['door'], 'z')
rect(1.4, 2.1, rightX-0.01, 1.05, L*0.30, COL['door'], 'x')

# --- Axes helper at front-left-floor corner ---
ax = (-W/2, 0, L/2)
add_edge(ax, (ax[0]+1, ax[1], ax[2]), COL['axisx'])
add_edge(ax, (ax[0], ax[1]+1, ax[2]), COL['axisy'])
add_edge(ax, (ax[0], ax[1], ax[2]-1), COL['axisz'])

# ---------------- Camera / projection ----------------
IW, IH = 1280, 960
fov = math.radians(55)
eye = (W*1.6, H*1.9, L*0.95)
tgt = (0, H*0.4, 0)
up = (0, 1, 0)

def sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    m = math.sqrt(a[0]**2+a[1]**2+a[2]**2) or 1.0
    return (a[0]/m,a[1]/m,a[2]/m)
def dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

f = norm(sub(tgt, eye))      # forward
r = norm(cross(f, up))       # right
u = cross(r, f)              # true up
aspect = IW/IH
fy = 1.0/math.tan(fov/2)
fx = fy/aspect

def project(p):
    d = sub(p, eye)
    cx = dot(d, r); cy = dot(d, u); cz = dot(d, f)  # cz = depth forward
    if cz <= 0.01: return None
    ndc_x = (cx/cz)*fx
    ndc_y = (cy/cz)*fy
    sx = (ndc_x*0.5+0.5)*IW
    sy = (1-(ndc_y*0.5+0.5))*IH
    return (sx, sy, cz)

# ---------------- Raster buffer ----------------
BG = (0x0b, 0x0e, 0x14)
buf = bytearray()
for _ in range(IW*IH):
    buf += bytes(BG)

def setpx(x, y, c):
    if 0 <= x < IW and 0 <= y < IH:
        i = (y*IW + x)*3
        buf[i:i+3] = bytes(c)

def line(p0, p1, c, thick=1):
    x0,y0 = p0; x1,y1 = p1
    x0,y0,x1,y1 = int(round(x0)),int(round(y0)),int(round(x1)),int(round(y1))
    dx = abs(x1-x0); dy = -abs(y1-y0)
    sx = 1 if x0<x1 else -1; sy = 1 if y0<y1 else -1
    err = dx+dy
    while True:
        for ox in range(-(thick//2), thick//2+1):
            for oy in range(-(thick//2), thick//2+1):
                setpx(x0+ox, y0+oy, c)
        if x0==x1 and y0==y1: break
        e2 = 2*err
        if e2>=dy: err+=dy; x0+=sx
        if e2<=dx: err+=dx; y0+=sy

# draw grid first (background), then everything else
def is_grid(c): return c == COL['grid']
for a,b,c in sorted(edges, key=lambda e: 0 if is_grid(e[2]) else 1):
    pa = project(a); pb = project(b)
    if not pa or not pb: continue
    th = 1 if is_grid(c) else 2
    line((pa[0],pa[1]), (pb[0],pb[1]), c, th)

# ---------------- PNG encode ----------------
def png(path, w, h, data):
    def chunk(typ, payload):
        return (struct.pack('>I', len(payload)) + typ + payload +
                struct.pack('>I', zlib.crc32(typ+payload) & 0xffffffff))
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += data[y*w*3:(y+1)*w*3]
    out = b'\x89PNG\r\n\x1a\n'
    out += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    out += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    out += chunk(b'IEND', b'')
    with open(path, 'wb') as fp:
        fp.write(out)

png('room-wireframe.png', IW, IH, buf)
print('wrote room-wireframe.png', IW, 'x', IH, 'edges:', len(edges))
