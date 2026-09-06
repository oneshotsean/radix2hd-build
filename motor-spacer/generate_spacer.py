#!/usr/bin/env python3
"""
Parametric motor spacer generator (pure Python, no dependencies).

Shape: a "clover" / rounded-diamond plate that follows the motor's own mounting
flange outline -- four bolt pads joined by concave-scalloped webs, with a large
open centre bore and four open windows between the arms.  The idea is that the
spacer covers no more of the motor base than the motor's own flange already
does, so cooling openings stay clear.

Outputs an STL (binary), an OpenSCAD source file and an SVG top view.

    python3 generate_spacer.py --out-dir .

All dimensions are millimetres.
"""

import argparse
import math
import os
import struct

# --------------------------------------------------------------------------
# outline maths
# --------------------------------------------------------------------------


class Profile:
    """Analytic 2D profile of the spacer, expressed as radius(angle)."""

    def __init__(self, pattern, pad_d, bore_d, web_w, screw_d, diagonal_pattern=False):
        # Bolt pattern.  `pattern` is the centre-to-centre distance between
        # ADJACENT holes (a square pattern), unless diagonal_pattern is set, in
        # which case it is the distance between OPPOSITE holes.
        if diagonal_pattern:
            self.bolt_r = pattern / 2.0
        else:
            self.bolt_r = math.hypot(pattern / 2.0, pattern / 2.0)

        self.pad_r = pad_d / 2.0
        self.bore_r = bore_d / 2.0
        self.screw_r = screw_d / 2.0
        self.web_w = web_w

        # Pads sit on the diagonals (45, 135, 225, 315 deg); the scalloped webs
        # sit between them (0, 90, 180, 270 deg).
        self.pad_angles = [math.radians(a) for a in (45.0, 135.0, 225.0, 315.0)]
        self.web_angles = [math.radians(a) for a in (0.0, 90.0, 180.0, 270.0)]

        # Concave scallop arc, tangent to the two pads it sits between, whose
        # closest approach to the centre leaves `web_w` of material outside the
        # bore.
        reach = self.bore_r + web_w
        px = self.bolt_r * math.cos(math.radians(45.0))
        py = self.bolt_r * math.sin(math.radians(45.0))
        k = self.pad_r - reach
        denom = 2.0 * px + 2.0 * k
        if denom <= 0:
            raise ValueError("web_w too large for this bolt pattern")
        self.scallop_d = (px * px + py * py - k * k) / denom
        self.scallop_r = self.scallop_d - reach
        if self.scallop_r <= 0:
            raise ValueError("web_w too large for this bolt pattern")

        # Angle at which the pad arc meets the scallop arc (the tangent point).
        vx, vy = px - self.scallop_d, py
        L = math.hypot(vx, vy)
        tx = self.scallop_d + self.scallop_r * vx / L
        ty = self.scallop_r * vy / L
        self.tangent_a = math.atan2(ty, tx)          # ~30.6 deg
        self.outer_r = self.bolt_r + self.pad_r      # max radius

        if self.bore_r + 0.1 >= self.bolt_r - self.screw_r:
            raise ValueError("centre bore runs into the screw holes")

    # -- ray/circle helper: distance from origin to circle centred at c ------
    @staticmethod
    def _roots(ux, uy, cx, cy, r):
        b = ux * cx + uy * cy
        disc = b * b - (cx * cx + cy * cy - r * r)
        if disc < 0.0:
            return None
        s = math.sqrt(disc)
        return b - s, b + s

    def outer(self, a):
        """Outer boundary radius at angle `a`."""
        ux, uy = math.cos(a), math.sin(a)
        phi = a % (math.pi / 2.0)                     # fold into one quadrant
        quad = a - phi
        if self.tangent_a <= phi <= (math.pi / 2.0 - self.tangent_a):
            # pad arc: circle centred on the bolt hole, far intersection
            ca = quad + math.pi / 4.0
            cx, cy = self.bolt_r * math.cos(ca), self.bolt_r * math.sin(ca)
            roots = self._roots(ux, uy, cx, cy, self.pad_r)
            return roots[1]
        # scallop arc: material is OUTSIDE the scallop circle, so the boundary
        # is the near intersection with whichever scallop this angle belongs to
        ca = quad if phi < math.pi / 4.0 else quad + math.pi / 2.0
        cx = self.scallop_d * math.cos(ca)
        cy = self.scallop_d * math.sin(ca)
        roots = self._roots(ux, uy, cx, cy, self.scallop_r)
        return roots[0]

    def screw_span(self, a):
        """(r_in, r_out) where the ray at angle `a` crosses a screw hole, else None."""
        ux, uy = math.cos(a), math.sin(a)
        for pa in self.pad_angles:
            cx, cy = self.bolt_r * math.cos(pa), self.bolt_r * math.sin(pa)
            b = ux * cx + uy * cy
            disc = b * b - (cx * cx + cy * cy - self.screw_r ** 2)
            if disc < -1e-7:
                continue
            if disc < 1e-7:
                disc = 0.0          # ray is tangent: the span pinches to a point
            s = math.sqrt(disc)
            if b + s > 0.0:
                return b - s, b + s
        return None

    def angles(self, segments=720):
        """Angular sample grid, including every exact feature transition."""
        out = set()
        for i in range(segments):
            out.add(i * 2.0 * math.pi / segments)
        half = math.asin(self.screw_r / self.bolt_r)   # screw hole silhouette
        for q in range(4):
            base = q * math.pi / 2.0
            out.add(base + self.tangent_a)
            out.add(base + math.pi / 2.0 - self.tangent_a)
            out.add(base + math.pi / 4.0 - half)
            out.add(base + math.pi / 4.0 + half)
        vals = sorted(x % (2.0 * math.pi) for x in out)
        # drop near-duplicates so no zero-width slices are produced
        keep = []
        for v in vals:
            if not keep or (v - keep[-1]) > 1e-9:
                keep.append(v)
        if (2.0 * math.pi - keep[-1]) < 1e-9:
            keep.pop()
        return keep


# --------------------------------------------------------------------------
# mesh construction
# --------------------------------------------------------------------------


def build_mesh(p, thickness, segments=720):
    """Return a list of (v0, v1, v2) triangles forming a closed solid.

    The plate is swept as angular slices.  Each ray carries the radial spans of
    solid material (one span normally, two where the ray crosses a screw hole),
    so top face, bottom face and every wall share the same vertices and the
    result is watertight by construction.
    """
    angs = p.angles(segments)
    n = len(angs)
    tris = []
    top, bot = thickness, 0.0

    def pt(a, r, z):
        return (r * math.cos(a), r * math.sin(a), z)

    def face(poly_xy):
        """poly_xy: CCW seen from above -> top face (+Z) and bottom face (-Z)."""
        t = [(x, y, top) for x, y in poly_xy]
        b = [(x, y, bot) for x, y in poly_xy]
        for k in range(1, len(poly_xy) - 1):
            tris.append((t[0], t[k], t[k + 1]))
            tris.append((b[0], b[k + 1], b[k]))

    def wall_out(a0, r0, a1, r1):
        """Wall whose normal faces away from the axis (outer edge, screw hole
        inner edge)."""
        v = [pt(a0, r0, bot), pt(a1, r1, bot), pt(a1, r1, top), pt(a0, r0, top)]
        tris.append((v[0], v[1], v[2]))
        tris.append((v[0], v[2], v[3]))

    def wall_in(a0, r0, a1, r1):
        """Wall whose normal faces towards the axis (bore, screw hole outer edge)."""
        v = [pt(a0, r0, bot), pt(a0, r0, top), pt(a1, r1, top), pt(a1, r1, bot)]
        tris.append((v[0], v[1], v[2]))
        tris.append((v[0], v[2], v[3]))

    spans = []
    for a in angs:
        s = p.screw_span(a)
        ro = p.outer(a)
        spans.append([(p.bore_r, ro)] if s is None
                     else [(p.bore_r, s[0]), (s[1], ro)])

    for i in range(n):
        j = (i + 1) % n
        a0, a1 = angs[i], angs[j]
        s0, s1 = spans[i], spans[j]

        if len(s0) == len(s1):
            for (lo0, hi0), (lo1, hi1) in zip(s0, s1):
                face([(math.cos(a0) * lo0, math.sin(a0) * lo0),
                      (math.cos(a0) * hi0, math.sin(a0) * hi0),
                      (math.cos(a1) * hi1, math.sin(a1) * hi1),
                      (math.cos(a1) * lo1, math.sin(a1) * lo1)])
        else:
            # One ray is exactly tangent to a screw hole, so it is split at the
            # tangent radius while its neighbour is not.  Emit a pentagon that
            # carries that extra vertex, otherwise a T-junction is left behind.
            if len(s0) == 2:
                rt = s0[0][1]
                lo, hi = s1[0]
                poly = [(a0, p.bore_r), (a0, rt), (a0, s0[1][1]), (a1, hi), (a1, lo)]
                apex = 4
            else:
                rt = s1[0][1]
                lo, hi = s0[0]
                poly = [(a0, lo), (a0, hi), (a1, s1[1][1]), (a1, rt), (a1, p.bore_r)]
                apex = 0
            xy = [(r * math.cos(a), r * math.sin(a)) for a, r in poly]
            xy = xy[apex:] + xy[:apex]
            face(xy)

        # outer wall
        wall_out(a0, s0[-1][1], a1, s1[-1][1])
        # centre bore wall
        wall_in(a0, p.bore_r, a1, p.bore_r)
        # screw hole wall (only across slices where both rays cross the hole)
        if len(s0) == 2 and len(s1) == 2:
            wall_out(a0, s0[0][1], a1, s1[0][1])   # side nearest the axis
            wall_in(a0, s0[1][0], a1, s1[1][0])    # side nearest the rim
    return tris


# --------------------------------------------------------------------------
# writers
# --------------------------------------------------------------------------


def write_stl(path, tris, header=b"motor spacer"):
    with open(path, "wb") as f:
        f.write(header[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / L, ny / L, nz / L,
                                a[0], a[1], a[2], b[0], b[1], b[2],
                                c[0], c[1], c[2], 0))


def write_svg(path, p, thickness, segments=720):
    """Top view, 1 unit = 1 mm, for a quick visual check."""
    R = p.outer_r + 2.0
    pts = []
    for i in range(segments):
        a = i * 2.0 * math.pi / segments
        r = p.outer(a)
        pts.append((r * math.cos(a) + R, R - r * math.sin(a)))
    d = "M " + " L ".join("%.3f,%.3f" % q for q in pts) + " Z"
    holes = []
    for pa in p.pad_angles:
        holes.append('<circle cx="%.3f" cy="%.3f" r="%.3f"/>'
                     % (p.bolt_r * math.cos(pa) + R, R - p.bolt_r * math.sin(pa), p.screw_r))
    holes.append('<circle cx="%.3f" cy="%.3f" r="%.3f"/>' % (R, R, p.bore_r))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{2*R:.1f}mm" height="{2*R+10:.1f}mm" viewBox="0 0 {2*R:.3f} {2*R+10:.3f}">
<rect width="100%" height="100%" fill="#ffffff"/>
<g fill="#2b2b2b" fill-rule="evenodd">
<path d="{d}"/>
{os.linesep.join(holes)}
</g>
<g fill="none" stroke="#c0392b" stroke-width="0.15" stroke-dasharray="0.8 0.6">
<circle cx="{R:.3f}" cy="{R:.3f}" r="{p.bolt_r:.3f}"/>
</g>
<text x="{R:.3f}" y="{2*R+7:.3f}" font-family="sans-serif" font-size="2.4" text-anchor="middle" fill="#2b2b2b">
{p.bolt_r*2*math.cos(math.radians(45))*1:.0f} mm hole spacing &#183; {thickness:.1f} mm thick &#183; {2*p.outer_r:.2f} mm across pads</text>
</svg>
"""
    with open(path, "w") as f:
        f.write(svg)


def write_scad(path, p, thickness, args):
    scad = f"""// Motor spacer -- {args.pattern:g} mm bolt pattern, {thickness:g} mm thick
// Generated by generate_spacer.py; edit the parameters and re-render (F6).

thickness   = {thickness:g};   // plate thickness
pattern     = {args.pattern:g};   // hole spacing, centre to centre{" (opposite holes)" if args.diagonal else " (adjacent holes)"}
screw_d     = {args.screw_d:g};  // clearance hole for M3
pad_d       = {args.pad_d:g};  // boss diameter around each screw
bore_d      = {args.bore_d:g}; // open centre
web_w       = {args.web_w:g};   // narrowest material between bore and outside
$fn         = 180;

bolt_r    = {"pattern/2" if args.diagonal else "sqrt(2)*pattern/2"};
pad_r     = pad_d/2;
bore_r    = bore_d/2;
reach     = bore_r + web_w;
px        = bolt_r*cos(45);
py        = bolt_r*sin(45);
k         = pad_r - reach;
scallop_d = (px*px + py*py - k*k) / (2*px + 2*k);
scallop_r = scallop_d - reach;
core_r    = bolt_r + pad_r - 2.7;   // filler disc, hidden under the real outline

linear_extrude(height = thickness)
difference() {{
    union() {{
        circle(r = core_r);
        for (a = [45:90:315]) translate([bolt_r*cos(a), bolt_r*sin(a)]) circle(r = pad_r);
    }}
    for (a = [0:90:270])
        translate([scallop_d*cos(a), scallop_d*sin(a)]) circle(r = scallop_r);
    circle(r = bore_r);
    for (a = [45:90:315])
        translate([bolt_r*cos(a), bolt_r*sin(a)]) circle(d = screw_d);
}}
"""
    with open(path, "w") as f:
        f.write(scad)


# --------------------------------------------------------------------------


def check_watertight(tris):
    """Every directed edge must appear exactly once, and its reverse once."""
    edges = {}
    q = lambda v: (round(v[0], 6), round(v[1], 6), round(v[2], 6))
    for tri in tris:
        a, b, c = (q(v) for v in tri)
        if a == b or b == c or a == c:
            continue                      # degenerate, contributes no surface
        for e in ((a, b), (b, c), (c, a)):
            edges[e] = edges.get(e, 0) + 1
    bad = 0
    for e, cnt in edges.items():
        if cnt != 1 or edges.get((e[1], e[0]), 0) != 1:
            bad += 1
    return bad, len(edges)


def volume(tris):
    v = 0.0
    for a, b, c in tris:
        v += (a[0] * (b[1] * c[2] - c[1] * b[2])
              - a[1] * (b[0] * c[2] - c[0] * b[2])
              + a[2] * (b[0] * c[1] - c[0] * b[1])) / 6.0
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thickness", type=float, default=2.0)
    ap.add_argument("--pattern", type=float, default=19.0,
                    help="hole spacing centre to centre (default: 19 mm between adjacent holes)")
    ap.add_argument("--diagonal", action="store_true",
                    help="treat --pattern as the distance between OPPOSITE holes")
    ap.add_argument("--screw-d", type=float, default=3.3, help="screw clearance hole")
    ap.add_argument("--pad-d", type=float, default=7.5, help="boss diameter around each screw")
    ap.add_argument("--bore-d", type=float, default=15.0, help="open centre diameter")
    ap.add_argument("--web-w", type=float, default=3.0, help="narrowest web width")
    ap.add_argument("--segments", type=int, default=720)
    ap.add_argument("--name", default=None)
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    p = Profile(args.pattern, args.pad_d, args.bore_d, args.web_w,
                args.screw_d, args.diagonal)
    tris = build_mesh(p, args.thickness, args.segments)
    bad, ne = check_watertight(tris)
    vol = volume(tris)

    name = args.name or ("motor_spacer_%gx%g_%gmm" % (args.pattern, args.pattern, args.thickness))
    os.makedirs(args.out_dir, exist_ok=True)
    stl = os.path.join(args.out_dir, name + ".stl")
    write_stl(stl, tris, name.encode())
    write_scad(os.path.join(args.out_dir, name + ".scad"), p, args.thickness, args)
    write_svg(os.path.join(args.out_dir, name + ".svg"), p, args.thickness, args.segments)

    print("%s: %d triangles, %d edges, %d unpaired, volume %.2f mm^3 (%.2f g in PETG)"
          % (name, len(tris), ne, bad, vol, vol * 1.27e-3))
    bbox = 2 * (p.bolt_r * math.cos(math.radians(45.0)) + p.pad_r)
    print("  max diameter %.2f mm (pad to pad), bounding box %.2f x %.2f mm,"
          " waist %.2f mm, bore %.2f mm"
          % (2 * p.outer_r, bbox, bbox, 2 * (p.bore_r + p.web_w), 2 * p.bore_r))


if __name__ == "__main__":
    main()
