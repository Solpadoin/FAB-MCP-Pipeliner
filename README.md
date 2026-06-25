# FAB MCP Pipeliner

Infrastructure for building repeatable Unreal Engine 5.3 FAB asset-pack projects from generated image sets.

The workflow is documented in [SKILL.md](SKILL.md). The repo contains:

- `templates/MedievalPaintings7.zip` - reusable UE template source, originally authored for UE 5.3.
- `scripts/fab_pipeline.py` - host-side project creation, showcase processing, validation, and zip packaging.
- `scripts/ue_fab_pipeline.py` - Unreal Python script executed inside UE 5.3 for plugin toggles, texture reimport, redirector cleanup, map loading, screenshot capture, and saves.
- `.codex/mcp.example.toml` - example MCP wiring for the selected UE MCP candidate.

Default project output root:

```text
C:\Unreal Engine Projects\FAB-ASSET-PACKS
```

Quick host-side help:

```powershell
python scripts\fab_pipeline.py --help
```
