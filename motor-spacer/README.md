# 2 mm motor spacer (16 × 16 mm bolt pattern, PETG-CF)

**Print this file:** [`motor_spacer_16x16_2mm.stl`](motor_spacer_16x16_2mm.stl) — four of them, one per
motor. Shape preview: [`motor_spacer_16x16_2mm.svg`](motor_spacer_16x16_2mm.svg).

![top view](motor_spacer_16x16_2mm.svg)

## Dimensions

| | |
|---|---|
| Thickness | **2.00 mm** |
| Bolt pattern | **16.00 mm** between adjacent holes, 22.63 mm across the diagonal |
| Screw holes | **Ø3.40 mm** (ISO 273 medium clearance for M3) |
| Bosses around the screws | Ø7.50 mm, 2.05 mm of material around each hole |
| Open centre | **Ø8.40 mm** — clears an 8 mm boss with 0.2 mm of radial slack |
| Waist (across the flats) | 14.40 mm |
| Max size | 30.13 mm pad-to-pad; sits inside a 23.5 × 23.5 mm square |
| Material used | ~0.58 cm³ ≈ 0.74 g of PETG each |

The bore is 8.4 rather than a dead-on 8.0 because FDM holes come out slightly undersize and a hole
printed at exactly the boss diameter is an interference fit. 0.2 mm of radial slack slips over an
8 mm boss while still being close enough to help centre the spacer as you start the screws.

## Shape

The outline follows the motor's own mounting flange: four bosses on the bolt circle, joined by
concave scalloped webs, centre open, four open windows between the arms. It covers little more than
the motor's own flange already covers.

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
  keep the first layer at 0.2 mm (0.2 + 15 × 0.12 = 2.00); a 0.12 first layer gives 16.67 layers and
  the slicer rounds you to 1.92 or 2.04.
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
python3 generate_spacer.py --pattern 16 --bore-d 8.4 --screw-d 3.4

python3 generate_spacer.py --pattern 16 --bore-d 8.4 --screw-d 3.4 --thickness 3   # 3 mm
python3 generate_spacer.py --pattern 16 --bore-d 12.4 --screw-d 3.4               # bigger boss
python3 generate_spacer.py --pattern 19 --diagonal --bore-d 9.0                   # Ø19 bolt circle
python3 generate_spacer.py --help
```

`--pattern` is the spacing between **adjacent** holes; `--diagonal` makes it the distance between
**opposite** holes instead.
