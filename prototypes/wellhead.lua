local aw = require("prototypes.aw-util")
local tex = require("prototypes.textures")

local base_drill = data.raw["mining-drill"]["pumpjack"]
local base_item = data.raw.item["pumpjack"]

local tiers = {
  {
    name = "antimatter-wellhead", -- tier 1: burns wood and other chemical fuel
    speed = 2,
    usage = "300kW",
    burner = true,
    order = "b[fluids]-b[antimatter-wellhead-1]",
    next = "antimatter-wellhead-2"
  },
  {
    name = "antimatter-wellhead-2", -- tier 2: electric
    speed = 6,
    usage = "400kW",
    order = "b[fluids]-b[antimatter-wellhead-2]",
    next = "antimatter-wellhead-3"
  },
  {
    name = "antimatter-wellhead-3", -- tier 3: advanced electric
    speed = 16,
    usage = "900kW",
    order = "b[fluids]-b[antimatter-wellhead-3]"
  }
}

for _, t in ipairs(tiers) do
  local e = table.deepcopy(base_drill)
  e.name = t.name
  e.minable = { mining_time = 0.5, result = t.name }
  e.resource_categories = { "antimatter-well" }
  e.mining_speed = t.speed
  e.energy_usage = t.usage
  e.fast_replaceable_group = "antimatter-wellhead"
  e.next_upgrade = t.next
  if t.burner then
    e.energy_source = aw.burner_source(2, 12)
    e.module_specification = nil
  else
    e.energy_source = {
      type = "electric",
      emissions_per_minute = 6,
      usage_priority = "secondary-input"
    }
  end

  -- textures: one static picture for all four rotations
  local pic = tex.animation("entity/antimatter-wellhead/" .. t.name .. ".png", tex.CONFIG.wellhead)
  e.animations = { north = pic, east = pic, south = pic, west = pic }
  e.base_picture = nil
  e.drawing_box = { { -2, -3.1 }, { 2, 1.6 } }
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
