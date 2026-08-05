;@AHK++UseV1
#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%
CoordMode, Mouse, Screen
CoordMode, Pixel, Screen
SendMode, Event
SetKeyDelay, 50, 50
SetMouseDelay, 50

COMM_PATH        := "..\communication.json"
PATHING_PATH     := "..\Pathing"
POLL_MS          := 100
FISHING_FAILSAFE := 31000
PATHING_FAILSAFE := 61000

Loop {
    Sleep, %POLL_MS%

    command := GetValue(COMM_PATH, "command")
    pathing := GetValue(COMM_PATH, "pathing")
    status  := GetValue(COMM_PATH, "status")

    FishingCycle := GetInt(COMM_PATH, "FishingCycle")
    SellCycle    := GetInt(COMM_PATH, "SellCycle")
    CurrentCycle := GetInt(COMM_PATH, "CurrentCycle")
    debug        := GetBool(COMM_PATH, "debug")

    if (command = "exit") {
        ReleaseKeys()
        ToolTip
        ExitApp
    }

    if (status != "busy")
        continue

    if (command = "fishing")
        GoSub, FishingSequence
}

FishingSequence:
    csvPath := PATHING_PATH . "\" . pathing . "\FishingPathing.csv"
    GoSub, PlayMovement

    Loop %FishingCycle% {
        if (GetValue(COMM_PATH, "status") != "busy")
            break

        debug := GetBool(COMM_PATH, "debug")

        MouseMove, 862, 843, 3
        Sleep, 300
        MouseClick, Left
        ShowTip(debug, "[Fishing] Casting...")
        Sleep, 300

        castTime := A_TickCount
        fishingFailsafeRan := false

        Loop {
            if (GetValue(COMM_PATH, "status") != "busy")
                break

            elapsed := A_TickCount - castTime

            if (elapsed >= FISHING_FAILSAFE && !fishingFailsafeRan) {
                ShowTip(debug, "[Fishing] Fishing failsafe - recasting...")

                MouseMove, 1268, 941, 3
                Sleep, 300
                MouseClick, Left
                Sleep, 300

                MouseMove, 1167, 476, 3
                Sleep, 300
                MouseClick, Left
                Sleep, 300

                MouseMove, 1113, 342, 3
                Sleep, 300
                MouseClick, Left
                Sleep, 300

                MouseMove, 862, 843, 3
                Sleep, 300
                MouseClick, Left

                fishingFailsafeRan := true
            }

            if (elapsed >= PATHING_FAILSAFE) {
                ShowTip(debug, "[Fishing] Pathing failsafe - repathing...")
                GoSub, PlayMovement
                break
            }

            PixelGetColor, color, 1176, 836, RGB
            if (color = 0xFFFFFF) {
                ShowTip(debug, "[Fishing] Bite detected!")
                MouseMove, 950, 880, 3
                Sleep, 50
                break
            }

            Sleep, 50
        }

        if (GetValue(COMM_PATH, "status") != "busy")
            break

        PixelGetColor, barColor, 955, 767, RGB
        ShowTip(debug, "[Fishing] Bar color: " . barColor)
        Sleep, 100

        miniStart := A_TickCount
        Loop {
            if (GetValue(COMM_PATH, "status") != "busy")
                break

            if (A_TickCount - miniStart >= 9000) {
                ShowTip(debug, "[Fishing] Minigame ended.")
                break
            }

            PixelSearch, FoundX, FoundY, 757, 762, 1161, 782, %barColor%, 5, Fast RGB
            if (ErrorLevel = 0) {
                ShowTip(debug, "[Fishing] In zone - holding")
            } else {
                MouseClick, Left
                ShowTip(debug, "[Fishing] Not in zone - clicking")
            }

            Sleep, 16
        }

        Sleep, 300
        MouseMove, 1113, 342, 3
        Sleep, 700
        MouseClick, Left
        ShowTip(debug, "[Fishing] Fish collected!")
        Sleep, 200

        CurrentCycle := GetInt(COMM_PATH, "CurrentCycle")
        CurrentCycle++
        WriteCurrentCycle(COMM_PATH, CurrentCycle)
    }

    if (GetValue(COMM_PATH, "status") = "busy") {
        csvPath := PATHING_PATH . "\" . pathing . "\SellingPathing.csv"
        GoSub, PlayMovement
        GoSub, SellInteraction
    }

    WriteValue(COMM_PATH, "done")
    ShowTip(debug, "[Fishing + Selling] Done.")
    Sleep, 2000
    ToolTip
return

SellInteraction:
    Loop %SellCycle% {
        if (GetValue(COMM_PATH, "status") != "busy")
            break

        debug := GetBool(COMM_PATH, "debug")

        MouseMove, 831, 401, 3
        Sleep, 200
        MouseClick, Left
        Sleep, 200

        ; Sell All button
        MouseMove, 650, 803, 3
        Sleep, 120
        MouseClick, Left
        Sleep, 180

        MouseMove, 791, 618, 3
        Sleep, 120
        MouseClick, Left
        Sleep, 650

        ShowTip(debug, "[Selling] Sell All " . A_Index . " / " . SellCycle)
    }
return

PlayMovement:
    if (!FileExist(csvPath)) {
        ShowTip(true, "[Pathing] Missing CSV: " . csvPath)
        Sleep, 2000
        return
    }

    Loop, Read, %csvPath%
    {
        if (A_Index = 1)
            continue

        line := Trim(A_LoopReadLine)
        if (line = "")
            continue

        parts := StrSplit(line, ",")

        type := Trim(GetCsvPart(parts, 1))
        key  := Trim(GetCsvPart(parts, 2))
        x    := Trim(GetCsvPart(parts, 3))
        y    := Trim(GetCsvPart(parts, 4))
        duration := Trim(GetCsvPart(parts, 5))

        if (duration = "")
            duration := "0"

        duration := duration + 0
        debug := GetBool(COMM_PATH, "debug")

        if (GetValue(COMM_PATH, "status") != "busy")
            break

        if (type = "press") {
            if (duration < 250)
                duration := 250

            SendEvent, {%key% down}
            ShowTip(debug, "[Pathing] press " . key . " for " . duration . "ms")
            Sleep, %duration%
            SendEvent, {%key% up}
            Sleep, 120
        }
        else if (type = "down") {
            SendEvent, {%key% down}
            ShowTip(debug, "[Pathing] down " . key)
            Sleep, 30
        }
        else if (type = "up") {
            SendEvent, {%key% up}
            ShowTip(debug, "[Pathing] up " . key)
            Sleep, 30
        }
        else if (type = "sleep") {
            if (duration <= 0 && key != "")
                duration := key + 0

            ShowTip(debug, "[Pathing] sleep " . duration . "ms")
            Sleep, %duration%
        }
        else if (type = "click") {
            if (key = "left")
                Click, %x%, %y%
            else
                Click, right, %x%, %y%

            if (duration < 50)
                duration := 50

            Sleep, %duration%
            SendEvent, {LButton up}
            SendEvent, {RButton up}
            Sleep, 120
        }
    }

    ReleaseKeys()
return

GetCsvPart(parts, index) {
    if (parts.Length() >= index)
        return parts[index]
    return ""
}

ReleaseKeys() {
    SendEvent, {w up}
    SendEvent, {a up}
    SendEvent, {s up}
    SendEvent, {d up}
    SendEvent, {r up}
    SendEvent, {e up}
    SendEvent, {i up}
    SendEvent, {o up}
    SendEvent, {Space up}
    SendEvent, {Escape up}
    SendEvent, {Enter up}
    SendEvent, {LButton up}
    SendEvent, {RButton up}
}

ShowTip(debug, msg) {
    if (debug)
        ToolTip, %msg%
    else
        ToolTip
}

GetValue(path, key) {
    FileRead, raw, %path%
    RegExMatch(raw, """" . key . """\s*:\s*""([^""]*)""", m)
    return m1
}

GetBool(path, key) {
    FileRead, raw, %path%
    RegExMatch(raw, """" . key . """\s*:\s*(true|false)", m)
    return (m1 = "true")
}

GetInt(path, key) {
    FileRead, raw, %path%
    RegExMatch(raw, """" . key . """\s*:\s*(\d+)", m)
    return m1 + 0
}

AtomicWrite(path, text) {
    tmp := path . ".tmp"

    FileDelete, %tmp%
    FileAppend, %text%, %tmp%
    FileMove, %tmp%, %path%, 1
}

WriteValue(path, status) {
    command := GetValue(path, "command")
    pathing := GetValue(path, "pathing")

    FishingCycle := GetInt(path, "FishingCycle")
    SellCycle    := GetInt(path, "SellCycle")
    CurrentCycle := GetInt(path, "CurrentCycle")

    debug := GetBool(path, "debug")
    debugStr := debug ? "true" : "false"

    out := "{`n"
        . "  ""command"": """ . command . """,`n"
        . "  ""pathing"": """ . pathing . """,`n"
        . "  ""status"": """ . status . """,`n"
        . "  ""FishingCycle"": " . FishingCycle . ",`n"
        . "  ""SellCycle"": " . SellCycle . ",`n"
        . "  ""CurrentCycle"": " . CurrentCycle . ",`n"
        . "  ""debug"": " . debugStr . "`n"
        . "}"

    AtomicWrite(path, out)
}

WriteCurrentCycle(path, cycle) {
    command := GetValue(path, "command")
    pathing := GetValue(path, "pathing")
    status  := GetValue(path, "status")

    FishingCycle := GetInt(path, "FishingCycle")
    SellCycle    := GetInt(path, "SellCycle")

    debug := GetBool(path, "debug")
    debugStr := debug ? "true" : "false"

    out := "{`n"
        . "  ""command"": """ . command . """,`n"
        . "  ""pathing"": """ . pathing . """,`n"
        . "  ""status"": """ . status . """,`n"
        . "  ""FishingCycle"": " . FishingCycle . ",`n"
        . "  ""SellCycle"": " . SellCycle . ",`n"
        . "  ""CurrentCycle"": " . cycle . ",`n"
        . "  ""debug"": " . debugStr . "`n"
        . "}"

    AtomicWrite(path, out)
}