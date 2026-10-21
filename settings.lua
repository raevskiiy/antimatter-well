data:extend({
  {
    type = "double-setting",
    name = "antimatter-cost-multiplier",
    setting_type = "startup",
    default_value = 1,
    minimum_value = 0.1,
    maximum_value = 100,
    order = "a"
  },
  {
    type = "double-setting",
    name = "antimatter-uranium-235-chance",
    setting_type = "startup",
    default_value = 0.007,
    minimum_value = 0.001,
    maximum_value = 1,
    order = "a2"
  },
  {
    type = "bool-setting",
    name = "antimatter-keep-offshore-pump",
    setting_type = "startup",
    default_value = false,
    order = "b"
  },
  {
    type = "bool-setting",
    name = "antimatter-remove-rocks",
    setting_type = "startup",
    default_value = true,
    order = "c"
  }
})
