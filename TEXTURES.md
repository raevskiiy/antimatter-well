# Antimatter Well – texture guide

All textures are already drawn (normal size and HD, ENABLE_HR is on). To restyle anything, overwrite the PNG
**keeping the same file name and the same pixel size**.
Transparent background, PNG (RGBA).

Scale: normal resolution = **32 px per tile**. HD (optional) = **64 px per tile** = exactly 2x the normal size,
file name gets the prefix `hr-`. HD files are used because `M.ENABLE_HR = true` in `prototypes/textures.lua`; set it to false to ignore them.

Sizes, positions and frame counts are all in `prototypes/textures.lua`.

## Icons (`graphics/icons/`, 64x64, one picture, no mipmaps)
antimatter-fluid.png, molten-iron.png, molten-copper.png, molten-stone.png, liquid-carbon.png, antimatter-well.png,
antimatter-wellhead.png, antimatter-wellhead-2.png, antimatter-wellhead-3.png,
matter-converter-burner.png, matter-converter.png, matter-converter-2.png,
matter-caster-burner.png, matter-caster.png, matter-caster-2.png,
isotope-separator.png

## Technology icons (`graphics/technology/`, 256x256)
antimatter-electric.png, antimatter-advanced.png

## Well on the ground (`graphics/entity/antimatter-well/`)
antimatter-well.png – 96x96 (HD: hr-antimatter-well.png, 192x192). Covers 3x3 tiles.
For an animation make a horizontal strip and set `frames` for `well` in textures.lua
(file width = 96 x frames).

## Wellhead, 3x3 tiles (`graphics/entity/antimatter-wellhead/`)
antimatter-wellhead.png, antimatter-wellhead-2.png, antimatter-wellhead-3.png – 128x144
(HD: hr-*.png, 256x288).
Canvas layout: the 96x96 footprint is the bottom of the canvas (x 16..112, y 48..144);
the top 48 px are free for a tall derrick. One picture is used for all four rotations.

## Matter converter, 2x3 tiles (`graphics/entity/matter-converter/`)
For each of matter-converter-burner, matter-converter, matter-converter-2 four pictures:
- `<name>-north.png` and `<name>-south.png` – 96x144 (HD 192x288), footprint 64x96 at x 16..80, y 48..144
- `<name>-east.png` and `<name>-west.png` – 144x112 (HD 288x224), footprint 96x64 at x 24..120, y 48..112

North: pipe inputs on top (2 tiles), outputs at the bottom. The other directions are the same layout rotated.
12 files for the normal size, 12 more for HD.

## Matter caster, 3x3 tiles (`graphics/entity/matter-caster/`)
For each of matter-caster-burner, matter-caster, matter-caster-2 four pictures:
`<name>-north.png`, `-east.png`, `-south.png`, `-west.png` – all 128x144 (HD 256x288),
same canvas layout as the wellhead (footprint 96x96 at x 16..112, y 48..144).
North: molten-material inputs on top, nothing on the other sides. 12 files normal size, 12 more for HD.

## Isotope separator, 3x3 tiles (`graphics/entity/isotope-separator/`)
`isotope-separator-north.png`, `-east.png`, `-south.png`, `-west.png` – all 128x144 (HD 256x288),
same canvas layout as the caster. One pipe input on the north side (hidden for recipes without fluid).
4 files normal size, 4 more for HD.

## Tips
- Keep your art inside the footprint described above (the bottom of each canvas); the part above it is for height.
- Shadows are not included; paint them into the picture if you want them.
- A missing or wrongly named file makes Factorio refuse to start with "Cannot load sprite".

## Regenerating
`python3 tools/build_textures.py graphics` (needs Pillow and numpy) redraws every file in this guide from code,
which overwrites hand-made edits.
