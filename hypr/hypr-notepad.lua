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
})

local function position_notepad(window)
    if window.title:match("^Hypr Notepad") then
        hl.exec_cmd("@POSITIONER@ " .. window.address)
    end
end

hl.on("window.open", position_notepad)
hl.on("window.title", position_notepad)
