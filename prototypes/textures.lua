-- All texture paths and sizes live here, so you can change them in one place.
-- See TEXTURES.md in the mod root for the full file list and canvas layout.

local ROOT = "__antimatter-well__/graphics/"
local M = {}

-- HD (hr-*) textures ship with the mod; set to false to use only the normal-size files.
-- The pictures come from tools/build_textures.py (python3 + Pillow + numpy); overwrite any file to restyle it.
M.ENABLE_HR = true

-- Canvas sizes in pixels at normal resolution (32 px = 1 tile). HR files are exactly 2x.
-- `shift` moves the canvas centre relative to the entity centre, in tiles (y grows downwards).
-- `frames` > 1 means the png is a horizontal strip of that many frames, each w x h.
M.CONFIG = {
  wellhead      = { w = 128, h = 144, shift = { 0, -0.75 }, frames = 1 }, -- 3x3 tiles
  converter_ns  = { w = 96,  h = 144, shift = { 0, -0.75 }, frames = 1 }, -- 2x3 tiles, facing north/south
  caster        = { w = 128, h = 144, shift = { 0, -0.75 }, frames = 1 }, -- 3x3 tiles, all four directions
  converter_ew  = { w = 144, h = 112, shift = { 0, -0.75 }, frames = 1 }, -- 3x2 tiles, facing east/west
  well          = { w = 96,  h = 96,  shift = { 0, 0 },     frames = 1 }  -- resource on the ground
}

function M.icon(name) return ROOT .. "icons/" .. name .. ".png" end
function M.tech_icon(name) return ROOT .. "technology/" .. name .. ".png" end

local function hr_path(path)
  return (path:gsub("([^/]+)$", "hr-%1"))
end

-- Sprite/animation for an entity. `rel_path` is relative to the graphics folder.
function M.animation(rel_path, cfg)
  local frames = cfg.frames or 1
  local file = ROOT .. rel_path
  local a = {
    filename = file,
    width = cfg.w,
    height = cfg.h,
    frame_count = frames,
    line_length = frames,
    shift = cfg.shift,
    priority = "high"
  }
  if M.ENABLE_HR then
    a.hr_version = {
      filename = hr_path(file),
      width = cfg.w * 2,
      height = cfg.h * 2,
      frame_count = frames,
      line_length = frames,
      shift = cfg.shift,
      scale = 0.5,
      priority = "high"
    }
  end
  return a
end

-- Sprite sheet for a resource entity (the well lying on the ground).
function M.resource_sheet(rel_path, cfg)
  local frames = cfg.frames or 1
  local file = ROOT .. rel_path
  local s = {
    filename = file,
    priority = "extra-high",
    width = cfg.w,
    height = cfg.h,
    frame_count = frames,
    variation_count = 1,
    shift = cfg.shift
  }
  if M.ENABLE_HR then
    s.hr_version = {
      filename = hr_path(file),
      priority = "extra-high",
      width = cfg.w * 2,
      height = cfg.h * 2,
      frame_count = frames,
      variation_count = 1,
      shift = cfg.shift,
      scale = 0.5
    }
  end
  return s
end

return M
