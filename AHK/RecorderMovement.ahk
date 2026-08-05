;@AHK++UseV1
#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%
CoordMode, Mouse, Screen
SendMode, Event
SetKeyDelay, 50, 50
SetMouseDelay, 50

; ── Config ────────────────────────────────────────────────
OUTPUT_FOLDER := "..\Pathing\EclipseDefault"
OUTPUT_FILE   := OUTPUT_FOLDER . "\SellingPathing.csv"

recording := false
recordedActions := []
heldKeys := {}
lastActionTime := 0

ToolTip, Recorder ready.`nF8 = Start/Stop Recording`nF9 = Save File`nF10 = Play File`nESC = Exit
SetTimer, ClearTip, -3500
return

; ── Hotkeys ───────────────────────────────────────────────

F8::
    recording := !recording

    if (recording) {
        recordedActions := []
        heldKeys := {}
        lastActionTime := A_TickCount
        ToolTip, Recording started
    } else {
        ReleaseAllRecordingKeys()
        ToolTip, Recording stopped.`nPress F9 to save.
    }

    SetTimer, ClearTip, -1800
return

F9::
    SaveRecording()
return

F10::
    PlayFile(OUTPUT_FILE)
return

F4::
    ReleaseAllRecordingKeys()
    ReleasePlaybackKeys()
    ExitApp
return

; ── Mouse Recording ───────────────────────────────────────

~LButton::
    if (!recording)
        return

    AddSleepSinceLastAction()

    MouseGetPos, mx, my
    recordedActions.Push({type: "click", key: "left", x: mx, y: my, duration: 120})
    lastActionTime := A_TickCount

    ToolTip, Recorded click: %mx%, %my%
    SetTimer, ClearTip, -500
return

~RButton::
    if (!recording)
        return

    AddSleepSinceLastAction()

    MouseGetPos, mx, my
    recordedActions.Push({type: "click", key: "right", x: mx, y: my, duration: 120})
    lastActionTime := A_TickCount

    ToolTip, Recorded right click: %mx%, %my%
    SetTimer, ClearTip, -500
return

; ── Key Recording ─────────────────────────────────────────

~w::StartKey("w")
~w up::StopKey("w")

~a::StartKey("a")
~a up::StopKey("a")

~s::StartKey("s")
~s up::StopKey("s")

~d::StartKey("d")
~d up::StopKey("d")

~Space::StartKey("Space")
~Space up::StopKey("Space")

~e::StartKey("e")
~e up::StopKey("e")

~r::StartKey("r")
~r up::StopKey("r")

~i::StartKey("i")
~i up::StopKey("i")

~o::StartKey("o")
~o up::StopKey("o")

~Enter::StartKey("Enter")
~Enter up::StopKey("Enter")

~Escape::StartKey("Escape")
~Escape up::StopKey("Escape")


; ── Recording Functions ───────────────────────────────────

StartKey(key) {
    global recording, heldKeys, recordedActions, lastActionTime

    if (!recording)
        return

    if (heldKeys.HasKey(key))
        return

    AddSleepSinceLastAction()

    heldKeys[key] := true
    recordedActions.Push({type: "down", key: key, x: "", y: "", duration: 0})
    lastActionTime := A_TickCount

    msg := "[REC] down " . key
    ToolTip, %msg%
    SetTimer, ClearTip, -500
}

StopKey(key) {
    global recording, heldKeys, recordedActions, lastActionTime

    if (!recording)
        return

    if (!heldKeys.HasKey(key))
        return

    AddSleepSinceLastAction()

    heldKeys.Delete(key)
    recordedActions.Push({type: "up", key: key, x: "", y: "", duration: 0})
    lastActionTime := A_TickCount

    msg := "[REC] up " . key
    ToolTip, %msg%
    SetTimer, ClearTip, -500
}

AddSleepSinceLastAction() {
    global recording, recordedActions, lastActionTime

    if (!recording)
        return

    if (lastActionTime = 0) {
        lastActionTime := A_TickCount
        return
    }

    elapsed := A_TickCount - lastActionTime

    ; Ignore tiny gaps so the CSV does not become noisy.
    if (elapsed >= 40)
        recordedActions.Push({type: "sleep", key: "", x: "", y: "", duration: elapsed})
}

ReleaseAllRecordingKeys() {
    global heldKeys, recordedActions, lastActionTime

    for key, value in heldKeys {
        AddSleepSinceLastAction()
        recordedActions.Push({type: "up", key: key, x: "", y: "", duration: 0})
        lastActionTime := A_TickCount
    }

    heldKeys := {}
}

SaveRecording() {
    global OUTPUT_FOLDER, OUTPUT_FILE, recordedActions

    FileCreateDir, %OUTPUT_FOLDER%
    FileDelete, %OUTPUT_FILE%
    FileAppend, type,key,x,y,duration`n, %OUTPUT_FILE%

    for i, action in recordedActions {
        line := action.type . "," . action.key . "," . action.x . "," . action.y . "," . action.duration . "`n"
        FileAppend, %line%, %OUTPUT_FILE%
    }

    msg := "Saved " . recordedActions.Length() . " actions.`n" . OUTPUT_FILE
    ToolTip, %msg%
    SetTimer, ClearTip, -2500
}

; ── Playback Test ─────────────────────────────────────────

PlayFile(path) {
    if (!FileExist(path)) {
        ToolTip, File not found:`n%path%
        SetTimer, ClearTip, -2000
        return
    }

    ToolTip, Playing file...
    SetTimer, ClearTip, -1000

    Loop, Read, %path%
    {
        if (A_Index = 1)
            continue

        line := Trim(A_LoopReadLine)
        if (line = "")
            continue

        parts := StrSplit(line, ",")

        type := Trim(GetCsvPart(parts, 1))
        key := Trim(GetCsvPart(parts, 2))
        x := Trim(GetCsvPart(parts, 3))
        y := Trim(GetCsvPart(parts, 4))
        duration := Trim(GetCsvPart(parts, 5))

        if (duration = "")
            duration := "0"

        duration := duration + 0

        if (type = "down") {
            SendEvent, {%key% down}
        }
        else if (type = "up") {
            SendEvent, {%key% up}
        }
        else if (type = "sleep") {
            Sleep, %duration%
        }
        else if (type = "press") {
            if (duration < 250)
                duration := 250

            SendEvent, {%key% down}
            Sleep, %duration%
            SendEvent, {%key% up}
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
        }
    }

    ReleasePlaybackKeys()
    ToolTip, Playback done.
    SetTimer, ClearTip, -1500
}

GetCsvPart(parts, index) {
    if (parts.Length() >= index)
        return parts[index]
    return ""
}

ReleasePlaybackKeys() {
    SendEvent, {w up}
    SendEvent, {a up}
    SendEvent, {s up}
    SendEvent, {d up}
    SendEvent, {r up}
    SendEvent, {e up}
    SendEvent, {i up}
    SendEvent, {o up}
    SendEvent, {Space up}
    SendEvent, {Enter up}
    SendEvent, {LButton up}
    SendEvent, {RButton up}
}

ClearTip:
    ToolTip
return