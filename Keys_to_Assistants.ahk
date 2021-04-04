#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

SetTitleMatchMode, 2
WinGet, Hwnd_List, List , Lineage

Hotkey, F5, LoopF5
Hotkey, F6, LoopF6
Hotkey, F7, LoopF7
Hotkey, F8, LoopF8
Hotkey, Up, LoopSendMove
return

LoopF5:
	Loop, %Hwnd_List%
	{
		Hwnd := Hwnd_List%A_Index%
		ControlSend,, {F5}, ahk_id %Hwnd%
	}
return

LoopF6:
	Loop, %Hwnd_List%
	{
		Hwnd := Hwnd_List%A_Index%
		ControlSend,, {F6}, ahk_id %Hwnd%
	}
return

LoopF7:
	Loop, %Hwnd_List%
	{
		Hwnd := Hwnd_List%A_Index%
		ControlSend,, {F7}, ahk_id %Hwnd%
	}
return

LoopF8:
	Loop, %Hwnd_List%
	{
		Hwnd := Hwnd_List%A_Index%
		ControlSend,, {F8}, ahk_id %Hwnd%
	}
return

LoopSendMove:
	Loop, %Hwnd_List%
	{
		Hwnd := Hwnd_List%A_Index%
		ControlSend,, {Up}, ahk_id %Hwnd%
	}
return

`::ExitApp

