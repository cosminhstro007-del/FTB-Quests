#!/usr/bin/env python3
"""Fix 26.3 FTB Library keyboard crash in the checked-out upstream source.

Minecraft 26.3's InputConstants.isKeyDown accepts an SDL *scancode*.
The original debug F3+B shortcut passes SDLKeycode.SDLK_F3, which is
a large SDL keycode and causes IndexOutOfBoundsException for any key
falling through BaseScreen.keyPressed.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_ftb-library")
file = root / "common/src/main/java/dev/ftb/mods/ftblibrary/client/gui/widget/BaseScreen.java"
text = file.read_text(encoding="utf-8")
old = "InputConstants.isKeyDown(SDLKeycode.SDLK_F3)"
new = "InputConstants.isKeyDown(SDLScancode.SDL_SCANCODE_F3)"
if old not in text:
    raise SystemExit("FTB Library upstream changed: expected SDL F3 expression not found")
if "import org.lwjgl.sdl.SDLKeycode;" not in text:
    raise SystemExit("FTB Library upstream changed: SDLKeycode import missing")
text = text.replace(old, new)
text = text.replace(
    "import org.lwjgl.sdl.SDLKeycode;",
    "import org.lwjgl.sdl.SDLKeycode;\nimport org.lwjgl.sdl.SDLScancode;"
)
file.write_text(text, encoding="utf-8")
print("Patched SDL F3 scancode issue:", file)
