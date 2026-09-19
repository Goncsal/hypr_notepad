hl.bind("ALT + N", hl.dsp.exec_cmd("@EXEC@"))

hl.window_rule({
    match = { title = "^New note$" },
    float = true,
    center = true,
})

hl.window_rule({
    match = { title = "^Hypr Notepad.*$" },
    float = true,
    size = { 360, 360 },
    move = { "monitor_w-window_w-(monitor_w*0.005)", "monitor_h*0.05037037" },
})

local function position_notepad(window)
    if window.title:match("^Hypr Notepad") then
        hl.exec_cmd("@POSITIONER@ " .. window.address)
    end
end

hl.on("window.open", position_notepad)
hl.on("window.open_early", position_notepad)
hl.on("window.title", position_notepad)
