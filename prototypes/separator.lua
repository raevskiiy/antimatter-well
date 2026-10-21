local tex = require("prototypes.textures")

-- Isotope separator: replaces the centrifuge. It takes over every "centrifuging" recipe
-- (Kovarex, nuclear fuel, reprocessing) and adds the antimatter -> uranium recipe.
local base_plant = data.raw["assembling-machine"]["chemical-plant"]
local base_item = data.raw.item["chemical-plant"]

data:extend({ { type = "recipe-category", name = "antimatter-isotope" } })

local e = table.deepcopy(base_plant)
e.name = "isotope-separator"
e.minable = { mining_time = 0.1, result = "isotope-separator" }
e.crafting_categories = { "antimatter-isotope", "centrifuging" }
e.crafting_speed = 1
e.energy_usage = "400kW"
e.next_upgrade = nil
e.fast_replaceable_group = nil

-- one fluid input (liquid antimatter); the pipe is hidden for recipes without fluids
for _, fb in ipairs(e.fluid_boxes) do
  if fb.production_type == "input" then
    e.fluid_boxes = { fb }
    break
  end
end
e.module_specification = { module_slots = 2 }

e.drawing_box = { { -2, -3.1 }, { 2, 1.6 } }
local function dir_pic(dir)
  return tex.animation("entity/isotope-separator/isotope-separator-" .. dir .. ".png", tex.CONFIG.caster)
end
e.animation = { north = dir_pic("north"), east = dir_pic("east"), south = dir_pic("south"), west = dir_pic("west") }
e.idle_animation = nil
e.working_visualisations = nil
e.icon = tex.icon("isotope-separator")
e.icon_size = 64
e.icon_mipmaps = nil
e.icons = nil

local item = table.deepcopy(base_item)
item.name = "isotope-separator"
item.place_result = "isotope-separator"
item.order = "g[isotope-separator]"
item.icon = tex.icon("isotope-separator")
item.icon_size = 64
item.icon_mipmaps = nil
item.icons = nil

data:extend({ e, item })
