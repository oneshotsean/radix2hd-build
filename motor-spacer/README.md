# 2 mm motor spacer (Ø19 mm bolt circle, PETG-CF)

**Print this file:** [`motor_spacer_19mm-bcd_2mm.stl`](motor_spacer_19mm-bcd_2mm.stl) — four of them,
one per motor. Shape preview: [`motor_spacer_19mm-bcd_2mm.svg`](motor_spacer_19mm-bcd_2mm.svg).

![top view](motor_spacer_19mm-bcd_2mm.svg)

## Dimensions

| | |
|---|---|
| Thickness | **2.00 mm** |
| Bolt circle | **Ø19.00 mm** — 13.44 mm between adjacent holes, 19.00 mm across opposite |
| Screw holes | **Ø3.70 mm** — deliberately oversized, see below |
| Bosses around the screws | Ø7.50 mm, 1.90 mm of material around each hole |
| Open centre | **Ø9.00 mm** — clears an 8 mm boss with 0.5 mm of radial slack |
| Waist (across the flats) | 15.00 mm |
| Max size | 26.50 mm pad-to-pad; sits inside a 20.94 × 20.94 mm square |
| Material used | ~0.47 cm³ ≈ 0.60 g of PETG each |

### Why the screw holes are Ø3.7 and not Ø3.3

The two numbers measured off the motor don't quite agree with each other: 19.00 mm across the
diagonal implies 13.435 mm between adjacent holes, while 13.00 mm between adjacent holes implies
18.385 mm across. The two readings put the bolt circle radius 0.31 mm apart, and a Ø3.3 hole only
gives an M3 screw 0.15 mm of radial slack — so building to either number risks the screws binding
if the other one was the accurate one.

Ø3.7 holes give ±0.35 mm of positional slack, which covers the full disagreement. The part is
built on the Ø19 bolt circle (the diagonal is the more reliable measurement, and it matches how
the XNOVA drawing dimensions the mount), and it will bolt up whichever reading turns out to be
right. Nothing is lost: the spacer is located by four screws in shear-free compression, not by
hole fit, and an M3 cap head still covers a Ø3.7 hole. A plain M3 washer under each head makes it
tidier if you have them.

## Shape

The outline follows the motor's own mounting flange: four bosses on the bolt circle, joined by
concave scalloped webs, centre wide open, four open windows between the arms. It covers little
more than the motor's own flange already covers.

## Before you print four

**Screw length.** A 2 mm spacer puts your motor screws 2 mm deeper into the motor. Go 2 mm longer
than stock and check they don't bottom out on the windings — that's the usual way a motor gets
killed after a spacer is fitted.

## Print settings

**PETG-CF, not PLA-CF.** The spacer is clamped against the motor's mounting face, which is the heat
path out of the stator. PLA's glass transition is ~55–60 °C and carbon fill doesn't move it; a motor
under load sits past that. Once it softens it creeps, the spacer thins under the screw heads,
preload drops, and the motor screws back themselves out in flight. PETG's ~80 °C Tg stays clear.
Plain PETG is ~95 % as good here.

- Flat on the bed, no supports.
- **0.2 mm layers with a 0.2 mm first layer** → 10 layers, exactly 2.00 mm. For a 0.12 mm profile,
  keep the first layer at 0.2 mm (0.2 + 15 × 0.12 = 2.00); a 0.12 first layer gives 16.67 layers
  and the slicer rounds you to 1.92 or 2.04.
- **4 perimeters, 100 % infill.** Solid is what you want under a screw head.
- 240–255 °C, bed 80 °C, hardened nozzle, dry filament.
- Add 0.2 mm elephant-foot compensation if your first layer squishes wide, so the bottoms of the
  screw holes don't close up.
- Print all four in one batch on the same settings — mismatched spacers tilt the motors slightly.

## Regenerating with different numbers

`generate_spacer.py` is pure Python, nothing to install. It writes the STL, an OpenSCAD source file
and the SVG preview, and verifies every mesh it produces is watertight.

```sh
# the file above
python3 generate_spacer.py --pattern 19 --diagonal --bore-d 9.0 --screw-d 3.7

# if the 13.00 mm adjacent reading turns out to be the accurate one
python3 generate_spacer.py --pattern 13 --bore-d 9.0 --screw-d 3.3

python3 generate_spacer.py --thickness 3        # thicker
python3 generate_spacer.py --help
```

`--pattern` is the spacing between **adjacent** holes; `--diagonal` makes it the distance between
**opposite** holes instead.
