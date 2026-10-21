local aw = require("prototypes.aw-util")
local tex = require("prototypes.textures")

-- Casting machine: molten metal in, plates / parts out. 3x3 like the chemical plant it is based on.
local base_plant = data.raw["assembling-machine"]["chemical-plant"]
local base_item = data.raw.item["chemical-plant"]

local tiers = {
  {
    name = "matter-caster-burner", -- burns wood and other chemical fuel
    speed = 1,
    usage = "200kW",
    burner = true,
    order = "f[matter-caster-1]",
    next = "matter-caster"
  },
  {
    name = "matter-caster", -- electric
    speed = 2,
    usage = "320kW",
    order = "f[matter-caster-2]",
    next = "matter-caster-2"
  },
  {
    name = "matter-caster-2", -- advanced electric
    speed = 5,
    usage = "650kW",
    order = "f[matter-caster-3]"
  }
}

for _, t in ipairs(tiers) do
  local e = table.deepcopy(base_plant)
  e.name = t.name
  e.minable = { mining_time = 0.1, result = t.name }
  e.crafting_categories = { "antimatter-casting" }
  e.crafting_speed = t.speed
  e.energy_usage = t.usage
  e.fast_replaceable_group = "matter-caster"
  e.next_upgrade = t.next
  if t.burner then
    e.energy_source = aw.burner_source(2, 15)
    e.module_specification = nil
    e.allowed_effects = nil
  end

  -- the caster only takes fluid in, so drop the chemical plant's two output pipes
  local inputs = {}
  for _, fb in ipairs(e.fluid_boxes) do
    if fb.production_type == "input" then inputs[#inputs + 1] = fb end
  end
  e.fluid_boxes = inputs

  e.drawing_box = { { -2, -3.1 }, { 2, 1.6 } }
  local function dir_pic(dir)
    return tex.animation("entity/matter-caster/" .. t.name .. "-" .. dir .. ".png", tex.CONFIG.caster)
  end
  e.animation = {
    north = dir_pic("north"),
    east = dir_pic("east"),
    south = dir_pic("south"),
    west = dir_pic("west")
  }
  e.idle_animation = nil
  e.working_visualisations = nil

  e.icon = tex.icon(t.name)
  e.icon_size = 64
  e.icon_mipmaps = nil
  e.icons = nil

  local item = table.deepcopy(base_item)
  item.name = t.name
  item.place_result = t.name
  item.order = t.order
  item.icon = tex.icon(t.name)
  item.icon_size = 64
  item.icon_mipmaps = nil
  item.icons = nil

  data:extend({ e, item })
end
