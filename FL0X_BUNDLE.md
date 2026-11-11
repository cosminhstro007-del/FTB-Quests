# FL0X FTB 26.3 experimental mod bundle

This branch assembles a single clean **mods/** folder with five NeoForge 26.3 jars:
FTB Library, FTB Teams, FTB Ranks, FTB Essentials, and FTB Quests.

The GitHub Actions workflow `package-ftb-suite-26.3.yml` compiles all five from their 26.3 development branches or the experimental Quests port, checks that the NeoForge JARs contain compiled classes and mod metadata, and packages **only** production JARs.

**Status:** compile-only; client/game integration not tested. Do not use on a production server yet. All original mod credit belongs to FTB Team.
