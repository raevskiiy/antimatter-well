local aw = require("prototypes.aw-util")
local tex = require("prototypes.textures")

local base_plant = data.raw["assembling-machine"]["chemical-plant"]
local base_item = data.raw.item["chemical-plant"]

local tiers = {
  {
    name = "matter-converter-burner", -- burns wood and other chemical fuel
    speed = 1,
    usage = "180kW",
    burner = true,
    order = "e[matter-converter-1]",
    next = "matter-converter"
  },
  {
    name = "matter-converter", -- electric
    speed = 2,
    usage = "300kW",
    order = "e[matter-converter-2]",
    next = "matter-converter-2"
  },
  {
    name = "matter-converter-2", -- advanced electric
    speed = 5,
    usage = "600kW",
    order = "e[matter-converter-3]"
  }
}

for _, t in ipairs(tiers) do
  local e = table.deepcopy(base_plant)
  e.name = t.name
  e.minable = { mining_time = 0.1, result = t.name }
  e.crafting_categories = { "antimatter-conversion" }
  e.crafting_speed = t.speed
  e.energy_usage = t.usage
  e.fast_replaceable_group = "matter-converter"
  e.next_upgrade = t.next
  if t.burner then
    e.energy_source = aw.burner_source(2, 15)
    e.module_specification = nil
    e.allowed_effects = nil
  end

  -- 2 wide x 3 tall (north/south), 3 x 2 when rotated
  e.collision_box = { { -0.85, -1.35 }, { 0.85, 1.35 } }
  e.selection_box = { { -1, -1.5 }, { 1, 1.5 } }
  e.drawing_box = { { -2, -3.1 }, { 2, 1.6 } }

  -- pipe connections: inputs on the top short side, outputs on the bottom short side.
  -- The chemical plant has them at x = -1 / 1 (3 wide); on a 2 wide body they sit at -0.5 / 0.5.
  for _, fb in ipairs(e.fluid_boxes) do
    for _, pc in ipairs(fb.pipe_connections) do
      pc.position = { pc.position[1] * 0.5, pc.position[2] }
    end
  end

  -- textures: separate pictures for each of the four directions
  local function dir_pic(dir, cfg)
    return tex.animation("entity/matter-converter/" .. t.name .. "-" .. dir .. ".png", cfg)
  end
  e.animation = {
    north = dir_pic("north", tex.CONFIG.converter_ns),
    east = dir_pic("east", tex.CONFIG.converter_ew),
    south = dir_pic("south", tex.CONFIG.converter_ns),
    west = dir_pic("west", tex.CONFIG.converter_ew)
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
