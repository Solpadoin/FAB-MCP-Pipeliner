from __future__ import annotations

import json
import sys
from pathlib import Path

import unreal


ALLOWED_TEXTURE_NAMES = {
    *(f"T_Photo_{index:02d}_D" for index in range(1, 7)),
    *(f"T_Picture_{index:02d}_D" for index in range(1, 12)),
}


def get_arg(prefix: str) -> str | None:
    for arg in sys.argv:
        if arg.startswith(prefix):
            return arg[len(prefix) :]
    return None


def load_config() -> dict:
    config_path = get_arg("-fab_config=")
    if not config_path:
        raise RuntimeError("Missing -fab_config=<path> argument")
    with open(config_path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def set_plugin_state(plugin_name: str, enabled: bool) -> None:
    plugins = unreal.Plugins.get()
    if plugins.is_plugin_enabled(plugin_name) == enabled:
        return
    if enabled:
        plugins.enable_plugin(plugin_name)
    else:
        plugins.disable_plugin(plugin_name)


def configure_plugins() -> None:
    # Required for this automation surface. Modeling Tools must stay disabled for generated packs.
    for required in ("PythonScriptPlugin", "EditorScriptingUtilities"):
        try:
            set_plugin_state(required, True)
        except Exception as exc:
            unreal.log_warning("Could not enable plugin {0}: {1}".format(required, exc))

    for modeling_plugin in ("ModelingToolsEditorMode", "MeshModelingToolset", "ModelingToolsEditorModeEditorOnly"):
        try:
            set_plugin_state(modeling_plugin, False)
        except Exception:
            pass


def rename_template_pack_folder(config: dict) -> None:
    old_folder = config.get("template_pack_folder")
    new_folder = config.get("pack_folder")
    if not old_folder or not new_folder or old_folder == new_folder:
        return

    old_path = "/Game/{0}".format(old_folder)
    new_path = "/Game/{0}".format(new_folder)
    if unreal.EditorAssetLibrary.does_directory_exist(new_path):
        return
    if unreal.EditorAssetLibrary.does_directory_exist(old_path):
        if not unreal.EditorAssetLibrary.rename_directory(old_path, new_path):
            raise RuntimeError("Failed to rename {0} to {1}".format(old_path, new_path))
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)


def reimport_texture(asset_path: str, source_file: str) -> None:
    asset_name = asset_path.rsplit("/", 1)[-1]
    if asset_name not in ALLOWED_TEXTURE_NAMES:
        raise RuntimeError("Refusing to reimport non-picture texture: {0}".format(asset_path))

    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if asset is None:
        raise RuntimeError("Texture asset not found: {0}".format(asset_path))

    source = Path(source_file)
    if not source.exists():
        raise RuntimeError("Source image not found: {0}".format(source))

    asset_import_data = asset.get_editor_property("asset_import_data")
    if asset_import_data:
        asset_import_data.scripted_add_filename(str(source), 0, "FAB generated source")

    task = unreal.AssetImportTask()
    destination_path, destination_name = asset_path.rsplit("/", 1)
    task.set_editor_property("filename", str(source))
    task.set_editor_property("destination_path", destination_path)
    task.set_editor_property("destination_name", destination_name)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", False)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False)


def fix_redirectors() -> None:
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    redirectors = registry.get_assets_by_class("ObjectRedirector", True)
    paths = [data.object_path for data in redirectors if str(data.package_path).startswith("/Game")]
    if not paths:
        return

    loaded = [unreal.EditorAssetLibrary.load_asset(str(path)) for path in paths]
    loaded = [asset for asset in loaded if asset is not None]
    if loaded:
        unreal.AssetToolsHelpers.get_asset_tools().fixup_referencers(loaded)


def load_demo_map(map_path: str) -> None:
    if not unreal.EditorLevelLibrary.load_level(map_path):
        raise RuntimeError("Failed to load demo map: {0}".format(map_path))


def take_high_res_screenshot(project_root: Path) -> Path:
    output = project_root / "DEMOSHOWCASE.png"
    if output.exists():
        output.unlink()

    unreal.SystemLibrary.execute_console_command(None, "HighResShot 1920x1080 filename=\"{0}\"".format(output))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    return output


def run() -> None:
    config = load_config()
    project_root = Path(config.get("projects_root", r"C:\Unreal Engine Projects\FAB-ASSET-PACKS")) / config["project_name"]

    configure_plugins()
    rename_template_pack_folder(config)
    fix_redirectors()

    for item in config.get("texture_reimports", []):
        reimport_texture(item["asset"], item["source"])

    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    fix_redirectors()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

    demo_map = config.get("demo_map") or "/Game/{0}/Maps/Demo".format(config["pack_folder"])
    load_demo_map(demo_map)
    unreal.EditorLevelLibrary.save_current_level()
    screenshot = take_high_res_screenshot(project_root)
    unreal.log("FAB demo screenshot requested: {0}".format(screenshot))


run()
