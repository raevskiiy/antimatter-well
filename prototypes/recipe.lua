local mult = settings.startup["antimatter-cost-multiplier"].value

local function fluid(name, amount, extra)
  local f = { type = "fluid", name = name, amount = amount }
  if extra then for k, v in pairs(extra) do f[k] = v end end
  return f
end

local function antimatter(amount)
  return fluid("antimatter-fluid", math.max(1, math.floor(amount * mult + 0.5)))
end

-- Units: 10 molten metal = 1 plate (1 ore in vanilla smelting terms).
--
-- Converter (speed 1): 10 antimatter/s in, 40 molten/s out  (= 4 plates/s of material)
-- Caster    (speed 1): 40 molten/s in, always (see the recipes below)
-- so one burner converter feeds exactly one burner caster, 12.8 stone furnaces worth of output.
-- 4 converters (iron, copper, carbon, water) draw 40 antimatter/s = the starting wellhead on the starting well.
--
-- `cost` = antimatter per craft, `time` = seconds per craft at crafting speed 1.
local conversions = {
  { id = "molten-iron",   cost = 10,  time = 1, result = fluid("molten-iron", 40),   enabled = true },
  { id = "molten-copper", cost = 10,  time = 1, result = fluid("molten-copper", 40), enabled = true },
  { id = "molten-stone",  cost = 10,  time = 1, result = fluid("molten-stone", 40),  enabled = true },
  { id = "liquid-carbon", cost = 10,  time = 1, result = fluid("liquid-carbon", 40), enabled = true },
  { id = "water",         cost = 10,  time = 1, result = fluid("water", 100, { temperature = 100 }), enabled = true }, -- comes out hot
  { id = "crude-oil",     cost = 20,  time = 1, result = fluid("crude-oil", 20),     enabled = false }  -- oil-processing
}

for _, c in ipairs(conversions) do
  data:extend({
    {
      type = "recipe",
      name = "antimatter-to-" .. c.id,
      localised_name = { "recipe-name.antimatter-to-" .. c.id },
      category = "antimatter-conversion",
      enabled = c.enabled,
      hide_from_player_crafting = true,
      energy_required = c.time,
      ingredients = { antimatter(c.cost) },
      results = { c.result },
      main_product = c.result.name,
      subgroup = "raw-resource",
      order = "z[antimatter]-" .. c.id
    }
  })
end

-- Uranium: no ore any more. The isotope separator (replaces the centrifuge) turns liquid antimatter
-- straight into uranium-235 (rare) or uranium-238. Same odds as the vanilla centrifuge recipe by default.
-- 12 s at speed 1 and 300 antimatter per craft = 25 antimatter/s per separator.
local u235 = settings.startup["antimatter-uranium-235-chance"].value
data:extend({
  {
    type = "recipe",
    name = "antimatter-to-uranium-isotopes",
    localised_name = { "recipe-name.antimatter-to-uranium-isotopes" },
    category = "antimatter-isotope",
    enabled = false, -- unlocked by uranium-processing
    hide_from_player_crafting = true,
    energy_required = 12,
    ingredients = { antimatter(300) },
    results = {
      { type = "item", name = "uranium-235", probability = u235, amount = 1 },
      { type = "item", name = "uranium-238", probability = 1 - u235, amount = 1 }
    },
    icon = "__base__/graphics/icons/uranium-processing.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "raw-material",
    order = "k[uranium-processing]-z[antimatter]"
  }
})

-- Kovarex replacement: no catalyst loop. 100 uranium-238 and liquid antimatter are enriched into uranium-235.
local ENRICH_U238 = 100     -- uranium-238 consumed
local ENRICH_U235 = 10      -- uranium-235 produced
local ENRICH_ANTIMATTER = 200
local ENRICH_TIME = 40      -- seconds at speed 1
data:extend({
  {
    type = "recipe",
    name = "antimatter-enrichment",
    localised_name = { "recipe-name.antimatter-enrichment" },
    category = "antimatter-isotope",
    enabled = false, -- unlocked by kovarex-enrichment-process
    hide_from_player_crafting = true,
    energy_required = ENRICH_TIME,
    ingredients = { { "uranium-238", ENRICH_U238 }, antimatter(ENRICH_ANTIMATTER) },
    results = { { type = "item", name = "uranium-235", amount = ENRICH_U235 } },
    main_product = "uranium-235",
    icon = "__base__/graphics/icons/kovarex-enrichment-process.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "intermediate-product",
    order = "r[uranium-processing]-c[kovarex-enrichment-process]-z[antimatter]",
    allow_decomposition = false
  }
})

-- Casting: molten material -> plates and parts. Every recipe eats 40 molten/s at crafting speed 1.
-- { product, count, molten fluid, molten amount, seconds, unlocked at start? }
local castings = {
  { "iron-plate",       5, "molten-iron",   50, 1.25, true  },
  { "copper-plate",     5, "molten-copper", 50, 1.25, true  },
  { "steel-plate",      1, "molten-iron",   50, 1.25, false }, -- steel-processing
  { "stone",            5, "molten-stone",  50, 1.25, true  },
  { "stone-brick",      1, "molten-stone",  20, 0.5,  true  },
  { "coal",             5, "liquid-carbon", 50, 1.25, true  },
  { "iron-gear-wheel",  1, "molten-iron",   20, 0.5,  true  },
  { "pipe",             1, "molten-iron",   10, 0.25, true  },
  { "iron-stick",       2, "molten-iron",   10, 0.25, true  },
  { "copper-cable",     2, "molten-copper", 10, 0.25, true  }
}

for _, c in ipairs(castings) do
  data:extend({
    {
      type = "recipe",
      name = "cast-" .. c[1],
      category = "antimatter-casting",
      enabled = c[6],
      hide_from_player_crafting = true,
      energy_required = c[5],
      ingredients = { fluid(c[3], c[4]) },
      results = { { type = "item", name = c[1], amount = c[2] } },
      main_product = c[1],
      subgroup = "raw-resource",
      order = "z[casting]-" .. c[1]
    }
  })
end

-- Machines ---------------------------------------------------------------

data:extend({
  {
    type = "recipe",
    name = "antimatter-wellhead",
    enabled = true,
    energy_required = 3,
    ingredients = { { "iron-plate", 15 }, { "pipe", 5 }, { "stone-furnace", 1 } },
    result = "antimatter-wellhead"
  },
  {
    type = "recipe",
    name = "matter-converter-burner",
    enabled = true,
    energy_required = 3,
    ingredients = { { "iron-plate", 10 }, { "pipe", 4 }, { "stone-furnace", 2 } },
    result = "matter-converter-burner"
  },
  {
    type = "recipe",
    name = "matter-caster-burner",
    enabled = true,
    energy_required = 3,
    ingredients = { { "iron-plate", 15 }, { "pipe", 5 }, { "stone-brick", 10 } },
    result = "matter-caster-burner"
  },
  {
    type = "recipe",
    name = "antimatter-wellhead-2",
    enabled = false,
    energy_required = 5,
    ingredients = { { "steel-plate", 10 }, { "electronic-circuit", 10 }, { "iron-gear-wheel", 10 }, { "pipe", 10 } },
    result = "antimatter-wellhead-2"
  },
  {
    type = "recipe",
    name = "matter-converter",
    enabled = false,
    energy_required = 5,
    ingredients = { { "steel-plate", 5 }, { "electronic-circuit", 5 }, { "iron-gear-wheel", 5 }, { "pipe", 5 } },
    result = "matter-converter"
  },
  {
    type = "recipe",
    name = "matter-caster",
    enabled = false,
    energy_required = 5,
    ingredients = { { "steel-plate", 5 }, { "electronic-circuit", 5 }, { "iron-gear-wheel", 5 }, { "stone-brick", 10 } },
    result = "matter-caster"
  },
  {
    type = "recipe",
    name = "isotope-separator",
    enabled = false, -- unlocked by uranium-processing
    energy_required = 4,
    ingredients = { { "concrete", 100 }, { "steel-plate", 50 }, { "advanced-circuit", 100 }, { "iron-gear-wheel", 100 } },
    result = "isotope-separator"
  },
  {
    type = "recipe",
    name = "antimatter-wellhead-3",
    enabled = false,
    energy_required = 10,
    ingredients = { { "antimatter-wellhead-2", 1 }, { "advanced-circuit", 10 }, { "steel-plate", 20 }, { "iron-gear-wheel", 20 }, { "pipe", 20 } },
    result = "antimatter-wellhead-3"
  },
  {
    type = "recipe",
    name = "matter-converter-2",
    enabled = false,
    energy_required = 8,
    ingredients = { { "matter-converter", 1 }, { "advanced-circuit", 5 }, { "steel-plate", 10 }, { "iron-gear-wheel", 10 } },
    result = "matter-converter-2"
  },
  {
    type = "recipe",
    name = "matter-caster-2",
    enabled = false,
    energy_required = 8,
    ingredients = { { "matter-caster", 1 }, { "advanced-circuit", 5 }, { "steel-plate", 10 }, { "iron-gear-wheel", 10 } },
    result = "matter-caster-2"
  }
})
