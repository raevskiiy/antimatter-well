-- Remove every vanilla ore / oil field from map generation.
local removed = { "iron-ore", "copper-ore", "coal", "stone", "uranium-ore", "crude-oil" }
for _, name in ipairs(removed) do
  local res = data.raw.resource[name]
  if res then res.autoplace = nil end
end

-- Hide the now useless sliders from the map generator screen (only the antimatter well slider stays).
for _, name in ipairs(removed) do
  data.raw["autoplace-control"][name] = nil
end

-- Map presets mention those controls by name; drop them so no preset points at a missing control.
local function strip_controls(t)
  if type(t) ~= "table" then return end
  if type(t.autoplace_controls) == "table" then
    for _, name in ipairs(removed) do t.autoplace_controls[name] = nil end
  end
  for _, v in pairs(t) do
    if type(v) == "table" then strip_controls(v) end
  end
end
strip_controls(data.raw["map-gen-presets"])

-- Rocks drop stone and coal, which would bypass the wells.
if settings.startup["antimatter-remove-rocks"].value then
  for _, name in ipairs({ "rock-huge", "rock-big", "sand-rock-big" }) do
    local rock = data.raw["simple-entity"][name]
    if rock then rock.autoplace = nil end
  end
end

-- Water comes from the antimatter converters, not the offshore pump.
if not settings.startup["antimatter-keep-offshore-pump"].value then
  local pump = data.raw.recipe["offshore-pump"]
  if pump then pump.enabled = false end
end

local function add_unlock(tech_name, recipe_name, drop_recipe)
  local tech = data.raw.technology[tech_name]
  if not tech then return end
  tech.effects = tech.effects or {}
  if drop_recipe then
    local kept = {}
    for _, eff in ipairs(tech.effects) do
      if not (eff.type == "unlock-recipe" and eff.recipe == drop_recipe) then
        kept[#kept + 1] = eff
      end
    end
    tech.effects = kept
  end
  table.insert(tech.effects, { type = "unlock-recipe", recipe = recipe_name })
end

-- Crude oil and uranium ore are unlocked by their usual technologies.
add_unlock("oil-processing", "antimatter-to-crude-oil", "pumpjack")

-- uranium-processing: the centrifuge and the ore recipe are replaced by the isotope separator.
do
  local tech = data.raw.technology["uranium-processing"]
  if tech then
    local kept = {}
    for _, eff in ipairs(tech.effects or {}) do
      if not (eff.type == "unlock-recipe" and (eff.recipe == "centrifuge" or eff.recipe == "uranium-processing")) then
        kept[#kept + 1] = eff
      end
    end
    table.insert(kept, { type = "unlock-recipe", recipe = "isotope-separator" })
    table.insert(kept, { type = "unlock-recipe", recipe = "antimatter-to-uranium-isotopes" })
    tech.effects = kept
  end
  -- nothing can build the centrifuge or mine/process ore any more
  for _, name in ipairs({ "centrifuge", "uranium-processing" }) do
    local r = data.raw.recipe[name]
    if r then r.enabled = false end
  end
end
-- Casting steel straight from molten iron comes with steel processing.
add_unlock("steel-processing", "cast-steel-plate")

-- Casters come with the material processing techs (steel furnace / electric furnace),
-- the furnaces themselves stay unlocked: the electric furnace is still an ingredient of production science.
add_unlock("advanced-material-processing", "matter-caster")
add_unlock("advanced-material-processing-2", "matter-caster-2")

-- Kovarex: the catalyst loop is replaced by direct enrichment of 100 uranium-238.
do
  local tech = data.raw.technology["kovarex-enrichment-process"]
  if tech then
    local kept = {}
    for _, eff in ipairs(tech.effects or {}) do
      if not (eff.type == "unlock-recipe" and eff.recipe == "kovarex-enrichment-process") then
        kept[#kept + 1] = eff
      end
    end
    table.insert(kept, { type = "unlock-recipe", recipe = "antimatter-enrichment" })
    tech.effects = kept
    tech.localised_description = { "technology-description.antimatter-enrichment" }
  end
  local r = data.raw.recipe["kovarex-enrichment-process"]
  if r then r.enabled = false end
end

-- There are no ores any more. Every non-smelting recipe that wanted an ore (vanilla: concrete wants
-- iron ore) takes the matching plate instead.
do
  local plate_for = { ["iron-ore"] = "iron-plate", ["copper-ore"] = "copper-plate" }
  local function fix(list)
    if type(list) ~= "table" then return end
    for _, ing in ipairs(list) do
      local name = ing.name or ing[1]
      if plate_for[name] then
        if ing.name then ing.name = plate_for[name] else ing[1] = plate_for[name] end
      end
    end
  end
  for _, recipe in pairs(data.raw.recipe) do
    if recipe.category ~= "smelting" then
      fix(recipe.ingredients)
      if recipe.normal then fix(recipe.normal.ingredients) end
      if recipe.expensive then fix(recipe.expensive.ingredients) end
    end
  end
end

-- Mining drills and pumpjacks have nothing to mine any more.
for _, name in ipairs({ "burner-mining-drill", "electric-mining-drill", "pumpjack" }) do
  local r = data.raw.recipe[name]
  if r then
    r.enabled = false
    r.hidden = true
  end
end
