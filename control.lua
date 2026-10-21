-- Places the first antimatter well near spawn and hands out the starting kit.

local WELL_AMOUNT = 600000 -- 200% yield (normal = 300000)

local function ensure_starting_well()
  global.antimatter = global.antimatter or {}
  if global.antimatter.well_position then return end

  local surface = game.surfaces["nauvis"]
  local force = game.forces["player"]
  if not (surface and force) then return end

  local spawn = force.get_spawn_position(surface)
  local target = { x = spawn.x + 8, y = spawn.y + 4 }

  surface.request_to_generate_chunks(target, 3)
  surface.force_generate_chunk_requests()

  local pos = surface.find_non_colliding_position("antimatter-wellhead", target, 40, 1, true)
  if not pos then pos = target end
  pos = { x = math.floor(pos.x) + 0.5, y = math.floor(pos.y) + 0.5 }

  -- clear anything that could block the 3x3 resource spot
  local area = { { pos.x - 3, pos.y - 3 }, { pos.x + 3, pos.y + 3 } }
  for _, e in pairs(surface.find_entities_filtered({ area = area, type = { "tree", "simple-entity", "cliff" } })) do
    e.destroy()
  end

  local well = surface.create_entity({
    name = "antimatter-well",
    position = pos,
    amount = WELL_AMOUNT,
    force = "neutral"
  })

  if well then
    global.antimatter.well_position = pos
    force.chart(surface, { { pos.x - 64, pos.y - 64 }, { pos.x + 64, pos.y + 64 } })
  end
end

local function setup_freeplay_items()
  if not remote.interfaces["freeplay"] then return end
  local items = remote.call("freeplay", "get_created_items")
  items["burner-mining-drill"] = nil
  items["antimatter-wellhead"] = 1
  items["matter-converter-burner"] = 2
  items["pipe"] = 10
  items["matter-caster-burner"] = 1
  items["stone-furnace"] = 2
  items["wood"] = 20
  remote.call("freeplay", "set_created_items", items)

  local respawn = remote.call("freeplay", "get_respawn_items")
  respawn["burner-mining-drill"] = nil
  remote.call("freeplay", "set_respawn_items", respawn)
end

script.on_init(function()
  setup_freeplay_items()
  ensure_starting_well()
end)

script.on_configuration_changed(function()
  ensure_starting_well()
end)

script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  local pos = global.antimatter and global.antimatter.well_position
  if player and pos then
    player.print({ "antimatter-well.intro", "[gps=" .. math.floor(pos.x) .. "," .. math.floor(pos.y) .. "]" })
  end
end)
