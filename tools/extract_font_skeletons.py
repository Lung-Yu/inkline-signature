"""用法：cd fonts && OUT=../site/hands.json python3 -I ../tools/extract_font_skeletons.py *.ttf
需要：pip install pillow numpy scipy scikit-image（Pillow 需支援 raqm）

Extract pen skeletons (centre line + radius + writing order) from script font glyphs."""
import json, math, sys, glob, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.morphology import skeletonize

S = 480  # px per em for rendering
CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&!?.-\''
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
N8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def render(font, ch):
    adv = font.getlength(ch)
    W, H = int(adv + 3*S), int(2.6*S)
    ox, oy = int(1.2*S), int(1.6*S)
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).text((ox, oy), ch, font=font, fill=255, anchor='ls')
    a = np.array(im) > 110
    return a, ox, oy, adv

def rdp(pts, eps):
    if len(pts) < 3: return pts
    a, b = np.array(pts[0][:2]), np.array(pts[-1][:2])
    ab = b - a; L = np.hypot(*ab)
    best, idx = -1, -1
    for i in range(1, len(pts)-1):
        p = np.array(pts[i][:2])
        d = abs(np.cross(ab, p-a))/L if L > 1e-9 else np.hypot(*(p-a))
        if d > best: best, idx = d, i
    if best > eps:
        return rdp(pts[:idx+1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]

def graph(sk):
    ys, xs = np.nonzero(sk)
    P = set(zip(ys.tolist(), xs.tolist()))
    nb = {p: [(p[0]+dy, p[1]+dx) for dy, dx in N8 if (p[0]+dy, p[1]+dx) in P] for p in P}
    # remove redundant diagonal adjacency (staircase) to keep degree honest
    for p in P:
        keep = []
        for q in nb[p]:
            if abs(q[0]-p[0]) + abs(q[1]-p[1]) == 2:
                if (p[0], q[1]) in P or (q[0], p[1]) in P: continue
            keep.append(q)
        nb[p] = keep
    for p in P:  # make symmetric
        nb[p] = [q for q in nb[p] if p in nb[q]]
    nodes = {p for p in P if len(nb[p]) != 2}
    edges, seen = [], set()
    for n in nodes:
        for q in nb[n]:
            if (n, q) in seen: continue
            path = [n, q]; prev, cur = n, q
            while cur not in nodes:
                nxt = [r for r in nb[cur] if r != prev]
                if not nxt: break
                prev, cur = cur, nxt[0]; path.append(cur)
            seen.add((path[-1], path[-2])); seen.add((n, q))
            edges.append(path)
    # pure cycles
    used = {p for e in edges for p in e}
    for p in P:
        if p in used or p in nodes: continue
        cyc = [p]; prev, cur = None, p
        while True:
            nxt = [r for r in nb[cur] if r != prev and (r not in cyc or (r == p and len(cyc) > 2))]
            if not nxt: break
            if p in nxt and len(cyc) > 2: cyc.append(p); break
            prev, cur = cur, nxt[0]; cyc.append(cur)
        used.update(cyc)
        if len(cyc) > 6: edges.append(cyc)
    return edges

def tangent(path, from_start=True, k=8):
    seg = path[:k] if from_start else path[::-1][:k]
    a, b = seg[0], seg[-1]
    v = np.array([b[1]-a[1], b[0]-a[0]], float)
    n = np.hypot(*v)
    return v/n if n > 0 else np.array([1.0, 0.0])

def plen(path):
    return sum(math.hypot(path[i][0]-path[i-1][0], path[i][1]-path[i-1][1]) for i in range(1, len(path)))

def extract(font, ch):
    a, ox, oy, adv = render(font, ch)
    if a.sum() == 0: return {'adv': adv/S, 'strokes': []}
    a = ndimage.binary_closing(a, iterations=1)
    dist = ndimage.distance_transform_edt(a)
    sk = skeletonize(a)
    edges = graph(sk)
    # prune spurs repeatedly
    for _ in range(3):
        deg = {}
        for e in edges:
            for p in (e[0], e[-1]): deg[p] = deg.get(p, 0) + 1
        out = []
        for e in edges:
            d0, d1 = deg[e[0]], deg[e[-1]]
            L = plen(e)
            junction = e[0] if d0 >= 3 else e[-1] if d1 >= 3 else None
            if junction is not None and (d0 == 1 or d1 == 1) and L < 1.6*dist[junction] + 3:
                continue
            out.append(e)
        if len(out) == len(edges): break
        edges = out
    # components
    adj = {}
    for i, e in enumerate(edges):
        for p in (e[0], e[-1]): adj.setdefault(p, []).append(i)
    comp_of, comps = {}, []
    for i in range(len(edges)):
        if i in comp_of: continue
        stack, c = [i], []
        while stack:
            j = stack.pop()
            if j in comp_of: continue
            comp_of[j] = len(comps); c.append(j)
            for p in (edges[j][0], edges[j][-1]):
                stack.extend(adj.get(p, []))
        comps.append(c)
    def cminx(c): return min(p[1] for j in c for p in edges[j])
    comps.sort(key=cminx)
    if not comps: return {'adv': adv/S, 'strokes': []}
    total = [sum(plen(edges[j]) for j in c) for c in comps]
    big = max(total)
    order = [c for c, t in zip(comps, total) if t > .18*big] + [c for c, t in zip(comps, total) if t <= .18*big]
    strokes = []
    for c in order:
        unused = set(c)
        pen = None
        while unused:
            # candidate start points: endpoints (degree 1) of unused edges, else any
            cand = []
            for j in unused:
                e = edges[j]
                for end in (0, -1):
                    p = e[end]
                    d = len([k for k in adj.get(p, []) if k in unused])
                    cand.append((d, p, j, end))
            if pen is None:
                ones = [c_ for c_ in cand if c_[0] == 1] or cand
                d, p, j, end = min(ones, key=lambda c_: c_[1][1] + .15*c_[1][0])
            else:
                ones = [c_ for c_ in cand if c_[0] == 1] or cand
                d, p, j, end = min(ones, key=lambda c_: math.hypot(c_[1][0]-pen[0], c_[1][1]-pen[1]))
            path = list(edges[j]) if end == 0 else list(edges[j][::-1])
            if path[0] == path[-1]:  # loop: go counter-clockwise on screen
                area = sum(path[i][1]*path[i+1][0] - path[i+1][1]*path[i][0] for i in range(len(path)-1))
                if area > 0: path = path[::-1]
            unused.discard(j)
            node = path[-1]
            trail = [(path[0], list(path))]
            while True:
                opts = [k for k in adj.get(node, []) if k in unused]
                if not opts:
                    # retrace (cusp): walk back along recent edges to a junction that still has unused edges
                    back, blen, found = [], 0, None
                    for st_node, epath in reversed(trail):
                        back += epath[::-1][1:]; blen += plen(epath)
                        if blen > .3*S: break
                        if [k for k in adj.get(st_node, []) if k in unused]: found = st_node; break
                    if found is None: break
                    path += back; node = found
                    continue
                tin = tangent(path, from_start=False)  # direction into node (reversed) -> flip
                tin = -tin
                best, bk, brev = 9, None, False
                for k in opts:
                    e = edges[k]
                    rev = e[0] != node
                    ep = e[::-1] if rev else e
                    tout = tangent(ep, True)
                    turn = math.acos(max(-1, min(1, float(np.dot(tin, tout)))))
                    if turn < best: best, bk, brev = turn, k, rev
                if best > 2.5: break
                e = edges[bk][::-1] if brev else edges[bk]
                trail.append((node, list(e)))
                path += e[1:]; unused.discard(bk); node = path[-1]
            pen = path[-1]
            pts = [(p[1], p[0], float(dist[p])) for p in path]
            pts = rdp(pts, 0.7)
            # resample radius along simplified points using neighbourhood max
            out = []
            for x, y, r in pts:
                out.append([round((x-ox)/S*1000), round((y-oy)/S*1000), round(max(r, .8)/S*1000*10)])
            if plen([(q[1], q[0]) for q in out]) < 4 and len(strokes) and len(out) < 3:
                pass
            strokes.append(out)
    return {'adv': adv/S, 'strokes': strokes}

def kern_table(font):
    k = {}
    for a in LETTERS:
        la = font.getlength(a)
        for b in LETTERS:
            v = font.getlength(a+b) - la - font.getlength(b)
            if abs(v) > .5: k[a+b] = round(v/S*1000)
    sp = font.getlength(' ')
    return k, sp/S

if __name__ == '__main__':
    fonts = sys.argv[1:]
    out = {}
    for f in fonts:
        font = ImageFont.truetype(f, S, layout_engine=ImageFont.Layout.RAQM)
        g = {ch: extract(font, ch) for ch in CHARS}
        k, sp = kern_table(font)
        out[f.split('/')[-1][:-4]] = {'g': {ch: [round(v['adv']*1000), v['strokes']] for ch, v in g.items()}, 'k': k, 'sp': round(sp*1000)}
        print(f, sum(len(v['strokes']) for v in g.values()), file=sys.stderr)
    dest = os.environ.get('OUT', 'hands.json')
    json.dump(out, open(dest, 'w'), separators=(',', ':'))
    print('wrote', dest, file=sys.stderr)
