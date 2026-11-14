-- Speed warning: a message on the screen while the bus is faster than a limit you choose
-- (in the launcher's Plugins page, or in the game's plugin settings panel).

local s = omsi.plugin.settings({
  { key = "limit", type = "number", label = "Warn above (km/h)", default = 50, min = 20, max = 120, step = 5 },
  { key = "only_on_duty", type = "bool", label = "Only while on a duty", default = false },
}, "Speed warning")

local limit, only_on_duty = s.limit, s.only_on_duty
local on_duty = false

omsi.on("setting", function(key, value)
  if key == "limit" then limit = value end
  if key == "only_on_duty" then only_on_duty = value end
end)
omsi.on("duty_start", function() on_duty = true end)
omsi.on("duty_end", function() on_duty = false end)

omsi.every(1, function()
  if only_on_duty and not on_duty then return end
  local kmh = omsi.var("Velocity")
  if kmh and kmh > limit then
    omsi.message(string.format("Slow down: %.0f km/h (limit %d)", kmh, limit), 1)
  end
end)
