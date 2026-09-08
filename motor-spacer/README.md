# 2 mm motor spacer (16 × 16 mm bolt pattern, PETG-CF)

**Print this file:** [`motor_spacer_16x16_2mm.stl`](motor_spacer_16x16_2mm.stl) — you need four of them
(one per motor). Quick look at the shape: [`motor_spacer_16x16_2mm.svg`](motor_spacer_16x16_2mm.svg).

![top view](motor_spacer_16x16_2mm.svg)

## Dimensions

| | |
|---|---|
| Thickness | **2.00 mm** |
| Screw pattern | 16.00 mm centre-to-centre between adjacent holes, **22.63 mm** across the diagonal |
| Screw holes | Ø3.30 mm (M3 clearance) |
| Bosses around the screws | Ø7.50 mm — 2.10 mm of material around each hole, more than an M3 cap head (Ø5.5) needs |
| Open centre | **Ø12.40 mm** — clears a 12.0 mm motor boss with 0.2 mm of radial slack |
| Waist (across the flats) | 18.40 mm |
| Max size | 30.13 mm pad-to-pad; sits inside a 23.5 × 23.5 mm square |
| Material used | ~0.58 cm³ ≈ 0.74 g of PETG each |

### Why the bore is 12.4 and not 12.0

A hole printed at exactly the boss diameter will not go on — FDM holes come out slightly undersize,
and zero clearance is an interference fit. 12.4 mm gives 0.2 mm of radial slack: it slips over a
12 mm boss but is still close enough to help centre the spacer while you start the screws. The
spacer is located by the four screws anyway, not by the bore.

## Shape

The outline follows the motor's own mounting flange: four bosses on the bolt circle, joined by
concave scalloped webs, with the centre wide open and four large open windows between the arms. It
covers essentially nothing the motor's mounting flange doesn't already cover — roughly 60 % less
area than a plain washer-style disc on the same bolt pattern.

At the four pad corners it reaches 30.13 mm across. If that overhangs your motor base by more than
you like, `--pad-d 6.8` pulls it in to 28.7 mm at the cost of some material around the screws.

## Before you print four

**Screw length.** A 2 mm spacer puts your motor screws 2 mm deeper into the motor. Go 2 mm longer
than stock and check they don't bottom out on the windings — that's the usual way a motor gets
killed after a spacer is fitted.

## Print settings

**PETG-CF**, not PLA-CF. The spacer is clamped against the motor's mounting face, which is the heat
path out of the stator. PLA's glass transition is ~55–60 °C and carbon fill doesn't move it; a
motor under load sits well past that. Once the material softens it creeps, the spacer thins under
the screw heads, preload drops and the motor screws back themselves out in flight. PETG's ~80 °C Tg
stays clear of that. Plain PETG is ~95 % as good here if that's what you have — the CF is buying
stiffness this part doesn't really need.

- Flat on the bed, no supports.
- **0.2 mm layers with a 0.2 mm first layer** → 10 layers, exactly 2.00 mm. If you'd rather run a
  0.12 mm profile, keep the first layer at 0.2 mm (0.2 + 15 × 0.12 = 2.00). A 0.12 mm first layer
  gives 16.67 layers and the slicer will round you to 1.92 or 2.04.
- **4 perimeters, 100 % infill.** Solid is what you want under a screw head.
- 240–255 °C, bed 80 °C, hardened nozzle, dry filament.
- No brim needed. If your first layer squishes wide, add 0.2 mm elephant-foot compensation so the
  bottom of the screw holes doesn't close up.
- Print all four in the same batch on the same settings so they're identical — mismatched spacers
  tilt the motors slightly.

## Regenerating with different numbers

Everything is parametric. `generate_spacer.py` is pure Python (nothing to install) and writes the
STL, an OpenSCAD source file and the SVG preview:

```sh
python3 generate_spacer.py --pattern 16 --bore-d 12.4    # the file above
python3 generate_spacer.py --pattern 16 --bore-d 12.4 --thickness 3   # 3 mm instead
python3 generate_spacer.py --pattern 16 --bore-d 12.4 --screw-d 3.5   # looser screw holes
python3 generate_spacer.py --pattern 19                  # 19 x 19 pattern
python3 generate_spacer.py --help
```

`--pattern` is the spacing between **adjacent** holes; add `--diagonal` to give the distance between
opposite holes instead. `motor_spacer_16x16_2mm.scad` is the same part as OpenSCAD source if you'd
rather edit it there.

The generator checks its own output — every STL it writes is verified watertight (zero unpaired
edges) and its mesh volume is cross-checked against the analytic area of the profile.
