# FAB Asset Pack Pipeline Skill

## Purpose

Use this skill to create UE 5.0.3 FAB asset-pack projects from generated image sets, reimport those images into template textures, validate the demo level visually, produce a marketplace-ready cover image, and package a clean zip archive.

Default workspace:

```text
C:\Unreal Engine Projects\FAB-ASSET-PACKS
```

Default engine:

```text
C:\Program Files\Epic Games\UE_5.0
```

## External MCP Choice

Preferred MCP candidate: `ChiR24/Unreal_mcp` (`https://github.com/ChiR24/Unreal_mcp`).

Selection reason:

- The project README states Unreal Engine `5.0-5.8` support.
- It exposes categories matching this pipeline: Asset Management, Editor Control, Level Management, System/console actions.
- It includes a native Unreal automation bridge and optional TypeScript bridge.

Fallback path: use Unreal Python through `scripts/ue_fab_pipeline.py`. This fallback is required for UE 5.0.3 reliability and is the authoritative implementation for this repository.

Do not use UE 5.8 official MCP for this workflow: it is too new for UE 5.0.3 projects.

## Required UE Operations

Only these UE operations are needed:

- Enable required editor scripting plugins for automation.
- Disable `ModelingToolsEditorMode` / Modeling Tools plugin for every generated project.
- Import or reimport generated image files into existing texture assets.
- Save changed packages.
- Fix up redirectors before packaging.
- Load the pack demo map.
- Capture a high-resolution screenshot.

## Project Creation

1. Create a pack config from `scripts/fab_config.example.json`.
2. Create the project from the template zip:

```powershell
python scripts\fab_pipeline.py create-project --config path\to\pack.json
```

3. Confirm the generated `.uproject` uses `EngineAssociation` `5.0`.
4. Confirm the project path is under:

```text
C:\Unreal Engine Projects\FAB-ASSET-PACKS
```

5. Open/resave in UE 5.0.3 to convert the template from 5.3-era assets when needed.
6. Do not rename the template content folder with filesystem tools. The Unreal automation step renames `/Game/<template_pack_folder>` to `/Game/<pack_folder>` inside the editor, then fixes redirectors.

## Image Generation Requirements

Generate 11 unique source images per asset pack. Produce 20 total texture imports by reusing selected images across the template's picture/photo texture slots.

Track every generated source image and target texture in the pack config under `texture_reimports`.

## Unreal Automation Run

Run UE 5.0.3 with the repository Unreal Python script:

```powershell
python scripts\fab_pipeline.py ue-command --config path\to\pack.json
```

The command prints the `UnrealEditor-Cmd.exe` invocation. Execute it when the config is ready.

The UE script must:

1. Disable Modeling Tools.
2. Enable Python/Editor scripting dependencies if missing.
3. Reimport each generated image into its target texture asset.
4. Save all touched assets.
5. Fix up redirectors under `/Game`.
6. Load the configured demo map.
7. Save the level.
8. Capture `DEMOSHOWCASE.png` into the project root.

MCP alternative: use the configured Unreal MCP to call equivalent tools for plugin state, asset import/reimport, level load, console command/screenshot, asset save, and redirector cleanup. If MCP tool names differ, call arbitrary editor Python through the MCP and execute `scripts/ue_fab_pipeline.py` logic inside the editor.

## Demo Screenshot Review

After the UE automation run, inspect:

```text
<ProjectRoot>\DEMOSHOWCASE.png
```

Validate visually:

- Every painting frame has a visible imported texture.
- There are no checkerboards, missing materials, blank placeholders, or broken imports.
- The demo level is the expected pack demo level.

If visual validation fails, fix imports and rerun the UE automation.

## Marketplace Cover

Use `DEMOSHOWCASE.png` as input for image editing with this prompt:

```text
Измени плейсхолдер стены на что-то подходящее для этой темматики. Формат изображения выполни 16:9. Сверху на английском название нашего ассет пака (например Medieval Paintings Pack Vol.1).

Снизу - разрешение наших картинок. Изображение должно быть понятным, читаемым, отлично подходящим в качестве обложки для маркетплейса FAB.
```

Then normalize the result:

```powershell
python scripts\fab_pipeline.py process-showcase --input path\to\edited.png --output path\to\FAB_Cover.jpg --title "Medieval Paintings Pack Vol.1" --resolution-label "2048x2048 PNG textures"
```

Final cover requirements:

- Exact dimensions: `1980x1920`.
- File size: at or below `3 MB`.
- Light compression is allowed if size is too large.

Note: the prompt asks for a 16:9 composition, while the required final file size is `1980x1920`. Treat this as a 16:9 visual composition placed within the required marketplace canvas.

## Content Cleanup And Validation

Before packaging:

1. Ensure the project is UE 5.0.3 / `EngineAssociation` `5.0`.
2. Ensure `Content` contains only the current asset-pack folder.
3. Remove `StarterContent` and all other unrelated content folders.
4. Run redirector cleanup again through UE before zipping.
5. Validate with:

```powershell
python scripts\fab_pipeline.py validate-project --config path\to\pack.json
```

## Packaging

Create the final zip:

```powershell
python scripts\fab_pipeline.py zip-project --config path\to\pack.json --output C:\path\to\PackName.zip
```

The archive must include:

- `.uproject`
- `Content`
- `Config`
- optional required project `Plugins`

The archive must exclude Unreal cache/generated folders:

- `Binaries`
- `DerivedDataCache`
- `Intermediate`
- `Saved`
- `.vs`

## Throughput Target

The pipeline is designed so a later run can produce 5-8 full asset packs within a 5 hour work window when image generation is available and the UE template conversion is stable.
