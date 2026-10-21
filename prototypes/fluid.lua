local tex = require("prototypes.textures")

local function molten(name, temperature, base, flow, order)
  return {
    type = "fluid",
    name = name,
    default_temperature = temperature,
    max_temperature = temperature,
    heat_capacity = "0.1KJ",
    base_color = base,
    flow_color = flow,
    icon = tex.icon(name),
    icon_size = 64,
    order = order
  }
end

data:extend({
  {
    type = "fluid",
    name = "antimatter-fluid",
    default_temperature = 25,
    heat_capacity = "0.1KJ",
    base_color = { r = 0.55, g = 0.15, b = 0.95 },
    flow_color = { r = 0.85, g = 0.55, b = 1.0 },
    icon = tex.icon("antimatter-fluid"),
    icon_size = 64,
    order = "a[fluid]-z[antimatter]"
  },
  -- Molten raw materials. Vanilla fluids with a temperature mechanic (water) come out hot,
  -- crude oil has none and stays as it is.
  molten("molten-iron",   1538, { r = 1.0, g = 0.45, b = 0.1 },  { r = 1.0, g = 0.8, b = 0.5 },  "a[fluid]-z[molten]-a[iron]"),
  molten("molten-copper", 1085, { r = 0.9, g = 0.4,  b = 0.2 },  { r = 1.0, g = 0.65, b = 0.4 }, "a[fluid]-z[molten]-b[copper]"),
  molten("molten-stone",  1200, { r = 0.8, g = 0.25, b = 0.1 },  { r = 1.0, g = 0.55, b = 0.3 }, "a[fluid]-z[molten]-c[stone]"),
  molten("liquid-carbon", 1200, { r = 0.15, g = 0.15, b = 0.2 }, { r = 0.4, g = 0.4, b = 0.5 },  "a[fluid]-z[molten]-d[carbon]"),
  { type = "recipe-category", name = "antimatter-conversion" },
  { type = "recipe-category", name = "antimatter-casting" }
})
