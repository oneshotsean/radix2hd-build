# 2 mm motor spacer (19 × 19 mm bolt pattern, PETG)

**Print this file:** [`motor_spacer_19x19_2mm.stl`](motor_spacer_19x19_2mm.stl) — you need four of them
(one per motor). Quick look at the shape: [`motor_spacer_19x19_2mm.svg`](motor_spacer_19x19_2mm.svg).

![top view](motor_spacer_19x19_2mm.svg)

## Dimensions

| | |
|---|---|
| Thickness | **2.00 mm** |
| Screw pattern | 19.00 mm centre-to-centre between **adjacent** holes (square), 26.87 mm across opposite holes |
| Screw holes | Ø3.30 mm (M3 clearance) |
| Bosses around the screws | Ø7.50 mm — 2.10 mm of material around each hole, more than an M3 cap head (Ø5.5) needs |
| Open centre | Ø15.00 mm |
| Waist (across the flats) | 21.00 mm |
| Max size | 34.37 mm pad-to-pad; sits inside a 26.5 × 26.5 mm square |
| Material used | ~0.71 cm³ ≈ 0.9 g of PETG each |

## Why it looks like that

The outline follows the motor's own mounting flange: four bosses on the bolt circle, joined by
concave scalloped webs, with the centre wide open and four large open windows between the arms.
It covers essentially nothing that the motor's mounting flange doesn't already cover — the Ø15 mm
centre bore keeps the hub area clear and the scallops between the screws leave the vent slots
between the arms open. A plain washer-style disc of the same bolt pattern would be a solid Ø34 mm
plate; this removes about 60 % of that area.

## Check these two things before printing four

1. **Centre boss clearance.** The bore is Ø15 mm. If the raised centre boss / bearing housing on
   your motor's mounting face is bigger than that, the spacer won't sit flat — regenerate with a
   larger `--bore-d` (see below).
2. **Screw length.** Adding a 2 mm spacer means your motor screws now sit 2 mm deeper into the
   motor. Go 2 mm longer than stock and check the screws don't bottom out on the windings — that
   is the usual way a motor gets killed after a spacer is fitted.

## Print settings (PETG)

- Flat on the bed, no supports needed. The tallest overhang is nothing — it's a flat plate.
- **0.2 mm layers, 10 layers total.** Or 0.25 mm layers × 8 if you prefer.
- **4 perimeters / 100 % infill.** At 2 mm thick and this small, perimeters alone should nearly
  fill it; solid is what you want under a screw head anyway.
- **No brim needed**, but if your first layer squishes wide, add a 0.2 mm elephant-foot
  compensation — otherwise the bottom of the screw holes ends up tight.
- If the M3 screws are a fight, run a 3.2 mm drill bit through by hand, or regenerate with
  `--screw-d 3.5`.
- Print them one at a time or with enough spacing that each layer has time to cool.

## Regenerating with different numbers

Everything is parametric. `generate_spacer.py` is pure Python (no libraries to install) and writes
the STL, an OpenSCAD source file and the SVG preview:

```sh
python3 generate_spacer.py --thickness 3            # a 3 mm spacer instead
python3 generate_spacer.py --bore-d 18              # bigger opening in the middle
python3 generate_spacer.py --screw-d 3.5            # looser screw holes
python3 generate_spacer.py --pattern 16             # 16 x 16 motor pattern
python3 generate_spacer.py --help                   # everything else
```

`motor_spacer_19x19_2mm.scad` is the same part as OpenSCAD source if you'd rather edit it there.

## If 19 mm meant the *other* measurement

The XNOVA drawing dimensions 19 mm between **adjacent** holes, which is also the standard 19 × 19
motor mount pattern, so that's what the main STL uses. If your holes are actually 19 mm apart
**straight across from each other** (opposite corners), print
[`alt/motor_spacer_19mm-diagonal_2mm.stl`](alt/motor_spacer_19mm-diagonal_2mm.stl) instead — same
design, 13.44 mm between adjacent holes, Ø11 mm centre bore, 26.5 mm max size.

Easiest way to tell them apart before printing: measure diagonally across the motor between two
holes that are opposite each other. ~26.9 mm → main file. ~19 mm → the alt file.
