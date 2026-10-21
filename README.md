# Antimatter Well

**Factorio 1.1 mod.** English | [Русский](README.ru.md)

All vanilla ore, coal, stone, uranium and crude oil are removed from the map. The only source of raw materials is the **antimatter well**: a wellhead pumps *liquid antimatter*, converters turn it into molten metal, hot water and crude oil, and casters turn the melt into plates and parts. The rest of the game (recipes, science, tech tree) stays vanilla.

> Status: early version (0.2.5). Balance is still being tuned, see [Known limitations](#known-limitations).

## How it works

```
antimatter well ──► wellhead ──► liquid antimatter ──► converter ──► molten iron / copper / stone,
                                                                     liquid carbon, hot water, crude oil
                                                          molten metal ──► caster ──► plates, gears, pipes, cables, steel, bricks, coal
```

1. You start next to a guaranteed well (200 % yield) with a starting kit: 1 wood-burning wellhead, 2 converters, 1 caster, 10 pipes, 2 stone furnaces and 20 wood.
2. Put the wellhead on the well, pipe it to a converter, pipe the converter to a caster. Pick a recipe in each machine and fuel the burner machines with wood. Wood is only needed to bootstrap: cast coal from liquid carbon and burn that.
3. Research electric and advanced versions to scale up. More wells are generated across the map; the setting "Antimatter well" in the map generator controls their frequency, size and richness.

### Machines (3 tiers each)

| Machine | Tier 1 (fuel) | Tier 2 (electric) | Tier 3 (advanced) |
|---|---|---|---|
| Wellhead (3x3) | speed x2 | x6 | x16 |
| Matter converter (2x3) | speed x1 | x2 | x5 |
| Matter caster (3x3) | speed x1 | x2 | x5 |
| Isotope separator (3x3) | one tier, electric | | |

- A wellhead gives 10 antimatter per second per unit of speed at 100 % well yield (tier 1 on the starting well: 40/s).
- A converter at speed 1 uses 10 antimatter/s and outputs 40 molten units/s (40 units = 4 plates). A caster at speed 1 consumes exactly 40 molten units/s, so a converter and a caster of the same tier match. One tier-1 pair replaces about 12.8 stone furnaces.
- Tier 2 and 3 are unlocked by the technologies *Electric antimatter extraction* (40 red science) and *Advanced antimatter extraction* (250 red + green + blue). Casters of tier 2 and 3 come with the vanilla techs *Advanced material processing* and *Advanced material processing 2*. Higher tiers fast-replace lower ones.

### Conversion recipes

| Recipe | Antimatter | Output |
|---|---:|---|
| Molten iron / copper / stone | 10 | 40 |
| Liquid carbon | 10 | 40 |
| Hot water (100 C) | 10 | 100 |
| Crude oil (after *Oil processing*) | 20 | 20 |

10 molten units = 1 plate of the same material. Casting recipes: iron plate, copper plate, stone, coal, stone brick, gear, pipe, iron stick, copper cable, steel plate (after *Steel processing*). Material cost always equals the vanilla recipe.

### Uranium and the nuclear chain

- No uranium ore. The **isotope separator** replaces the centrifuge: 300 antimatter gives 1 uranium-235 (0.7 %, configurable) or 1 uranium-238 (99.3 %) in 12 s.
- *Uranium processing* unlocks the separator instead of the centrifuge. It also runs all other centrifuge recipes (nuclear fuel, fuel reprocessing).
- *Kovarex enrichment* is replaced by direct enrichment: 100 uranium-238 + 200 antimatter give 10 uranium-235 in 40 s.

### Other changes to vanilla

- Offshore pump, mining drills and pumpjack recipes are disabled (nothing to mine). The offshore pump can be re-enabled in the settings.
- Concrete takes an iron plate instead of iron ore. Every non-smelting recipe that wants ore takes the plate instead.
- Rocks are removed because they drop stone and coal (setting).
- Resource sliders for iron, copper, stone, coal, uranium and crude oil are removed from the map generator; only the antimatter well slider remains.

## Installation

1. Download `antimatter-well_0.2.5.zip` from the [Releases](../../releases) page. Do not unpack it.
2. Put the zip into the Factorio `mods` folder:
   - Windows: `%appdata%\Factorio\mods`
   - Linux: `~/.factorio/mods`
   - macOS: `~/Library/Application Support/factorio/mods`
3. Start Factorio, enable the mod and create a **new** map. The mod changes map generation and is not meant to be added to an existing save.

Requires Factorio 1.1 and the base game. No other dependencies.

## Settings (startup)

| Setting | Default | Meaning |
|---|---|---|
| Antimatter cost multiplier | 1 | Multiplies the antimatter needed by every conversion recipe |
| Chance of uranium-235 | 0.007 | Chance that the separator gives U-235 instead of U-238 |
| Keep offshore pump recipe | off | Allow vanilla water pumping |
| Remove rocks | on | Rocks would give stone and coal without wells |

## Textures

The mod ships all graphics (normal and HD, `hr-*` files). File names, sizes and the canvas layout are in [TEXTURES.md](TEXTURES.md); `tools/build_textures.py` redraws them from code. Overwrite any PNG with the same name and size to restyle it.

## Known limitations

- Balance was calculated but not play-tested to the end of the tech tree. Tell us if something runs short or piles up.
- The mod is intended for a fresh game; adding it to an existing save is not supported.
- Wellheads use one picture for all four rotations, so the pipe stub does not follow the rotation.
- Not compatible with mods that need vanilla ore or oil patches.
- The `description` in `info.json` is outdated (it still mentions ores) and will be updated in the next version.

## Contributing

Issues and pull requests are welcome. When changing recipes, keep the rule "10 molten units = 1 plate" and the converter/caster throughput match (40 units/s per speed point).

## License

Not chosen yet. Add a `LICENSE` file before publishing.
