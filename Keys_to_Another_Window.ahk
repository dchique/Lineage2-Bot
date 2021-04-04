#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

SetTitleMatchMode, 2
WinGet, Hwnd_List, List , Lineage

Hotkey, \, Wheels
return

1::
ControlSend,, {F1}, ahk_id 525856
return
2:: 
ControlSend,, {F2}, ahk_id 525856
return
3:: 
ControlSend,, {F3}, ahk_id 525856
return
4:: 
ControlSend,, {F4}, ahk_id 525856
return
5:: 
ControlSend,, {F5}, ahk_id 525856
return
6:: 
ControlSend,, {F6}, ahk_id 525856
return
7:: 
ControlSend,, {F7}, ahk_id 525856
return
8:: 
ControlSend,, {F8}, ahk_id 525856
9:: 
ControlSend,, {F9}, ahk_id 525856
return
0:: 
ControlSend,, {F10}, ahk_id 525856
return
-:: 
ControlSend,, {F11}, ahk_id 525856
return
=:: 
ControlSend,, {F12}, ahk_id 525856
return



Wheels:
	{
		Send, {WheelUp 4}
	}
return

`::ExitApp

