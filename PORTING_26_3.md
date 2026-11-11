# Unofficial NeoForge 26.3 port (work in progress)

This is an experimental **source-only port** of FTB Quests from Minecraft 26.1.2 to 26.3.

## Current progress

- Updated Minecraft and NeoForge version/range to **26.3**.
- Updated Loom and NeoForge ModDev plugin versions to match FTB's existing 26.3 development branches.
- Updated the FTB Library and FTB Teams dependency coordinates to their expected 26.3 **SNAPSHOT** versions.
- Added independent GitHub Actions compilation for **NeoForge only**, without publishing credentials.
- GitHub Actions successfully builds **FTB Library 26.3** and **FTB Teams 26.3** from upstream branches. Teams needs a small temporary 26.3 network buffer patch, applied in CI.
- First Quests compilation reached Java and reported **76 errors** (before the first Quests source-fix batch).

**Current status:** FTB Library and Teams SNAPSHOT artifacts are built locally inside CI because they are not publicly available from the checked Maven repositories. FTB Quests still has unresolved Java 26.3 API errors. Client/server startup, GUI, quest editor, tasks, rewards, networking and saves are **not validated**.

## Verification

From a checkout with Java 25 available:

```sh
./gradlew :neoforge:classes :neoforge:jar --stacktrace --no-daemon
```

The workflow runs the same command and uploads a JAR only if compilation succeeds. A successful build does **not** prove in-game compatibility.

## Upstream code and attribution

Original project: https://github.com/FTBTeam/FTB-Quests

FTB Quests is authored by **FTB Team**. Upstream describes the mod as **All Rights Reserved**; this experimental fork is not an official FTB release and makes no claim of license or trademark ownership. Do not redistribute compiled JARs without confirming permission.

## Next stages

1. [x] Build matching FTB Library / Teams 26.3 SNAPSHOT artifacts locally in the CI job.
2. [ ] Fix source/API compile errors introduced in Minecraft 26.3 (first batch: inventory prediction, pose transformations, LWJGL classpath).
3. Verify NeoForge client in a single-player world: quest menu, editing, tasks and rewards.
4. Verify integrated-server persistence and multiplayer/client-server sync.
