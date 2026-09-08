# 2 mm motor spacer (Ø19.63 mm bolt circle, PETG-CF)

**Print this file:** [`motor_spacer_v2_2mm.stl`](motor_spacer_v2_2mm.stl) — four of them, one per
motor. Shape preview: [`motor_spacer_v2_2mm.svg`](motor_spacer_v2_2mm.svg).

![top view](motor_spacer_v2_2mm.svg)

The hole positions here come from a measured correction off a printed part that was test-fitted on
the motor, not from a caliper reading of the motor itself. The previous revision's holes sat 1.5 mm
too far out; every hole has been moved 1.5 mm straight in toward the centre.

## Dimensions

| | |
|---|---|
| Thickness | **2.00 mm** |
| Bolt circle | **Ø19.6274 mm** — 13.879 mm between adjacent holes |
| Hole centres | (±6.9393, ±6.9393) mm from the centre |
| Screw holes | Ø3.40 mm (ISO 273 medium clearance for M3) |
| Bosses around the screws | Ø7.50 mm, 2.05 mm of material around each hole |
| Open centre | Ø8.40 mm — clears an 8 mm boss with 0.2 mm of radial slack |
| Waist (across the flats) | 14.40 mm |
| Max size | 27.13 mm pad-to-pad; sits inside a 21.38 × 21.38 mm square |
| Material used | ~0.50 cm³ ≈ 0.64 g of PETG each |

### Checking it before you print four

Measure the diagonal between two opposite holes on the printed part, centre to centre: it should be
**19.63 mm**, against 22.63 mm on the previous revision. Adjacent holes should read 13.88 mm.

## Shape

Four bosses on the bolt circle joined by concave scalloped webs, centre open, four open windows
between the arms — so the spacer covers little more than the motor's own mounting flange.

## Before you print four

**Screw length.** A 2 mm spacer puts your motor screws 2 mm deeper into the motor. Go 2 mm longer
than stock and check they don't bottom out on the windings.

## Print settings

**PETG-CF, not PLA-CF.** The spacer is clamped against the motor's mounting face, which is the heat
path out of the stator. PLA's glass transition is ~55–60 °C and carbon fill doesn't move it; a motor
under load sits past that. Once it softens it creeps, the spacer thins under the screw heads,
preload drops, and the motor screws back themselves out in flight. PETG's ~80 °C Tg stays clear.

- Flat on the bed, no supports.
- **0.2 mm layers with a 0.2 mm first layer** → 10 layers, exactly 2.00 mm. For a 0.12 mm profile
  keep the first layer at 0.2 mm (0.2 + 15 × 0.12 = 2.00).
- **4 perimeters, 100 % infill.**
- 240–255 °C, bed 80 °C, hardened nozzle, dry filament.
- Add 0.2 mm elephant-foot compensation if your first layer squishes wide.
- Print all four in one batch on the same settings.

## Regenerating with different numbers

`generate_spacer.py` is pure Python, nothing to install. It writes the STL, an OpenSCAD source file
and the SVG preview, and verifies every mesh it produces is watertight.

```sh
# the file above
python3 generate_spacer.py --pattern 19.6274 --diagonal --bore-d 8.4 --screw-d 3.4

# to nudge the holes again: change the --pattern number by 2x the radial move you want,
# e.g. another 0.5 mm in per hole -> --pattern 18.6274
```

`--pattern` is the spacing between **adjacent** holes; `--diagonal` makes it the distance between
**opposite** holes instead.
