local M = {}

-- Keys of a prototype that hold sprites we are allowed to recolour.
-- (working_visualisations are left alone so recipe tinting still works.)
local GRAPHIC_KEYS = { "animations", "animation", "idle_animation", "base_picture" }

local function tint_layers(t, tint)
  if type(t) ~= "table" then return end
  if t.filename and not t.draw_as_shadow and not t.tint then
    t.tint = tint
  end
  for _, v in pairs(t) do
    if type(v) == "table" then tint_layers(v, tint) end
  end
end

function M.tint_entity(entity, tint)
  for _, key in ipairs(GRAPHIC_KEYS) do
    if entity[key] then tint_layers(entity[key], tint) end
  end
end

-- Replace icon/icon_size/icon_mipmaps with a tinted `icons` layer.
function M.tint_icon(proto, tint)
  local icon = proto.icon
  local size = proto.icon_size or 64
  local mips = proto.icon_mipmaps or 4
  proto.icon = nil
  proto.icon_size = nil
  proto.icon_mipmaps = nil
  proto.icons = { { icon = icon, icon_size = size, icon_mipmaps = mips, tint = tint } }
end

function M.burner_source(fuel_slots, emissions)
  return {
    type = "burner",
    fuel_category = "chemical",
    effectivity = 1,
    fuel_inventory_size = fuel_slots,
    emissions_per_minute = emissions,
    smoke = {
      {
        name = "smoke",
        deviation = { 0.1, 0.1 },
        frequency = 3,
        position = { 0, -2 },
        starting_vertical_speed = 0.0,
        starting_frame_deviation = 60
      }
    }
  }
end

return M
