#!/usr/bin/env python3
"""Create a verified FTB NeoForge 26.3 bundle from CI-compiled JARs only."""
from pathlib import Path
import shutil
import zipfile

package = Path("FL0X_FTB_26_3")
mods = package / "mods"
mods.mkdir(parents=True, exist_ok=True)

components = {
    "ftb-library": ("_ftb-library/neoforge/build/libs", "dev/ftb/mods/ftblibrary/"),
    "ftb-teams": ("_ftb-teams/neoforge/build/libs", "dev/ftb/mods/ftbteams/"),
    "ftb-ranks": ("_ftb-ranks/neoforge/build/libs", "dev/ftb/mods/ftbranks/"),
    "ftb-essentials": ("_ftb-essentials/neoforge/build/libs", "dev/ftb/mods/ftbessentials/"),
    "ftb-quests": ("neoforge/build/libs", "dev/ftb/mods/ftbquests/"),
}

manifest = []
for mod, (directory, classes_prefix) in components.items():
    files = [
        p for p in Path(directory).glob("*.jar")
        if not p.name.endswith(("-sources.jar", "-javadoc.jar", "-dev.jar", "-slim.jar"))
        and not p.name.endswith("-plain.jar")
    ]
    if len(files) != 1:
        raise SystemExit(f"Expected exactly one production JAR for {mod}; found {files}")
    jar = files[0]
    with zipfile.ZipFile(jar) as archive:
        names = archive.namelist()
        if not any(n.startswith(classes_prefix) and n.endswith(".class") for n in names):
            raise SystemExit(f"{jar}: missing expected {mod} compiled classes")
        if "META-INF/neoforge.mods.toml" not in names:
            raise SystemExit(f"{jar}: not a NeoForge mod JAR (no neoforge.mods.toml)")
    shutil.copy2(jar, mods / jar.name)
    manifest.append((mod, jar.name))
    print(f"OK: {mod}: {jar.name} ({jar.stat().st_size} bytes)")

if len(list(mods.glob("*.jar"))) != 5:
    raise SystemExit("The bundle must contain exactly five JAR files")

readme = """FL0X FTB MODS - Minecraft 26.3 / NeoForge
============================================
Experimental compile-only bundle.
Place the FIVE JAR files from this 'mods' folder into the instance's mods folder.

Includes:
- FTB Library (required dependency)
- FTB Teams (required by Quests)
- FTB Ranks (optional for Essentials, included as requested)
- FTB Essentials
- FTB Quests

JAVA: 25
MINECRAFT: 26.3
MOD LOADER: NeoForge 26.3

CAUTION:
Source builds passed GitHub Actions, but the combined suite has NOT been tested
inside Minecraft. Back up your worlds and configs before testing. Do NOT use
in your production server until tested. The custom FTB Teams network bridge
and FTB Quests GUI adaptations are experimental.

License and credit: FTB Team (upstream authors); unofficial experimental builds.
Do not redistribute publicly without confirming upstream redistribution rights.
"""
(package / "CITESTE-MA.txt").write_text(readme)
(package / "LISTA_JAR.txt").write_text(
    "\n".join(f"{mod}: {filename}" for mod, filename in manifest) + "\n"
)
print("Package validated: five NeoForge mod JARs, no sources/Javadocs.")
