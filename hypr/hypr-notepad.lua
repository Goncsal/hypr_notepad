hl.bind("ALT + N", hl.dsp.exec_cmd("@EXEC@"))

hl.window_rule({
    match = { class = "^io\\.github\\.goncsal\\.HyprNotepad$" },
    float = true,
    center = true,
    size = { 720, 480 },
})
