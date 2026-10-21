local resource_autoplace = require("resource-autoplace")
local tex = require("prototypes.textures")

resource_autoplace.initialize_patch_set("antimatter-well", false)

data:extend({
  { type = "resource-category", name = "antimatter-well" },
  {
    type = "autoplace-control",
    name = "antimatter-well",
    localised_name = { "", "[entity=antimatter-well] ", { "entity-name.antimatter-well" } },
    richness = true,
    order = "b-g",
    category = "resource"
  }
})

local well = table.deepcopy(data.raw.resource["crude-oil"])
well.name = "antimatter-well"
well.category = "antimatter-well"
well.order = "a-b-b"
well.minimum = 100000
well.normal = 300000
well.infinite_depletion_amount = 1
well.map_color = { 0.7, 0.25, 1 }
well.minable.results = {
  {
    type = "fluid",
    name = "antimatter-fluid",
    amount_min = 10,
    amount_max = 10,
    probability = 1
  }
}
well.autoplace = resource_autoplace.resource_autoplace_settings({
  name = "antimatter-well",
  order = "b",
  base_density = 8.2,
  base_spots_per_km2 = 3.5,
  random_probability = 1 / 48,
  random_spot_size_minimum = 1,
  random_spot_size_maximum = 1,
  additional_richness = 220000,
  has_starting_area_placement = false,
  regular_rq_factor_multiplier = 1
})

well.icon = tex.icon("antimatter-well")
well.icon_size = 64
well.icon_mipmaps = nil
well.icons = nil
well.stages = { sheet = tex.resource_sheet("entity/antimatter-well/antimatter-well.png", tex.CONFIG.well) }

data:extend({ well })
