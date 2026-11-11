#!/usr/bin/env python3
"""Adapt FTB Library's legacy GLFW mouse-button mapping to SDL3 input in MC 26.3.

The 26.3 SDLEventHandler feeds raw SDL_MouseButtonEvent.button (1=left, 2=middle,
3=right, 4=X1, 5=X2) into MouseButtonEvent. FTB Library's internal MouseButton
enum still uses GLFW-style IDs (0=left, 1=right, 2=middle, 3=back, 4=next).
Translate at the screen wrapper boundary, preserving the legacy internal IDs
used elsewhere by the library and by FTB Quests.
"""
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "_ftb-library")
base = root / "common/src/main/java/dev/ftb/mods/ftblibrary"

def patch(relative, replacements):
    file = base / relative
    src = file.read_text(encoding="utf-8")
    for before, after in replacements:
        count = src.count(before)
        if count != 1:
            raise SystemExit(f"{relative}: expected exactly one match for {before!r}; got {count}")
        src = src.replace(before, after, 1)
    file.write_text(src, encoding="utf-8")
    print("patched:", file)

patch("client/gui/input/MouseButton.java", [(
    """    public int hashCode() {""",
    """    /**
     * Convert raw SDL3 mouse button IDs (Minecraft 26.3) to internal
     * GLFW-compatible logical IDs used by existing FTB widgets.
     */
    public static MouseButton fromSDL(int button) {
        return switch (button) {
            case 1 -> LEFT;   // SDL_BUTTON_LEFT
            case 2 -> MIDDLE; // SDL_BUTTON_MIDDLE
            case 3 -> RIGHT;  // SDL_BUTTON_RIGHT
            case 4 -> BACK;   // SDL_BUTTON_X1
            case 5 -> NEXT;   // SDL_BUTTON_X2
            default -> get(button);
        };
    }

    public int hashCode() {"""
)])

patch("client/gui/widget/ScreenWrapper.java", [
    ("if (event.button() == MouseButton.BACK.id)", "if (MouseButton.fromSDL(event.button()) == MouseButton.BACK)"),
    ("return wrappedGui.mousePressed(MouseButton.get(event.button())) || super.mouseClicked(event, flag);",
     "return wrappedGui.mousePressed(MouseButton.fromSDL(event.button())) || super.mouseClicked(event, flag);"),
    ("wrappedGui.mouseReleased(MouseButton.get(event.button()));",
     "wrappedGui.mouseReleased(MouseButton.fromSDL(event.button()));"),
    ("return wrappedGui.mouseDragged(mouseButtonEvent.button(), dragX, dragY) || super.mouseDragged(mouseButtonEvent, dragX, dragY);",
     "return wrappedGui.mouseDragged(MouseButton.fromSDL(mouseButtonEvent.button()).id, dragX, dragY) || super.mouseDragged(mouseButtonEvent, dragX, dragY);")
])
patch("client/gui/MenuScreenWrapper.java", [
    ("wrappedGui.updateMouseOver((int) event.x(), (int) event.x());",
     "wrappedGui.updateMouseOver((int) event.x(), (int) event.y());"),
    ("if (event.button() == MouseButton.BACK.id)", "if (MouseButton.fromSDL(event.button()) == MouseButton.BACK)"),
    ("return wrappedGui.mousePressed(MouseButton.get(event.button())) || super.mouseClicked(event, flag);",
     "return wrappedGui.mousePressed(MouseButton.fromSDL(event.button())) || super.mouseClicked(event, flag);"),
    ("wrappedGui.mouseReleased(MouseButton.get(event.button()));",
     "wrappedGui.mouseReleased(MouseButton.fromSDL(event.button()));")
])

# SDL mouse state is a bitmask indexed by raw 1-based SDL button IDs.
# The existing FTB Widget implementation incorrectly shifts by (legacyId - 1),
# so dragging the left mouse button tests bit 31 instead of SDL bit 0.
patch("client/gui/widget/Widget.java", [(
    """        int mask = 1 << (button.id - 1);""",
    """        int sdlId = switch (button.id) {
            case 0 -> 1; // logical left -> SDL left
            case 1 -> 3; // logical right -> SDL right
            case 2 -> 2; // logical middle -> SDL middle
            case 3 -> 4; // logical back -> SDL X1
            case 4 -> 5; // logical next -> SDL X2
            default -> button.id;
        };
        int mask = sdlId >= 1 && sdlId <= 32 ? 1 << (sdlId - 1) : 0;"""
)])
