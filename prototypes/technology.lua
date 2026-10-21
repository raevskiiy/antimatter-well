local tex = require("prototypes.textures")

data:extend({
  {
    type = "technology",
    name = "antimatter-electric",
    icon = tex.tech_icon("antimatter-electric"),
    icon_size = 256,
    prerequisites = { "electronics", "steel-processing" },
    effects = {
      { type = "unlock-recipe", recipe = "antimatter-wellhead-2" },
      { type = "unlock-recipe", recipe = "matter-converter" }
    },
    unit = {
      count = 40,
      ingredients = { { "automation-science-pack", 1 } },
      time = 15
    },
    order = "a-a-a"
  },
  {
    type = "technology",
    name = "antimatter-advanced",
    icon = tex.tech_icon("antimatter-advanced"),
    icon_size = 256,
    prerequisites = { "antimatter-electric", "advanced-electronics", "chemical-science-pack" },
    effects = {
      { type = "unlock-recipe", recipe = "antimatter-wellhead-3" },
      { type = "unlock-recipe", recipe = "matter-converter-2" }
    },
    unit = {
      count = 250,
      ingredients = {
        { "automation-science-pack", 1 },
        { "logistic-science-pack", 1 },
        { "chemical-science-pack", 1 }
      },
      time = 30
    },
    order = "a-a-b"
  }
})
