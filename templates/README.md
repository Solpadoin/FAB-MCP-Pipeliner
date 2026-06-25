# Templates

`MedievalPaintings7.zip` is the reusable asset-pack template provided with the task.

Known facts from inspection:

- UE project file: `MedievalPaintings7.uproject`
- Declared `EngineAssociation`: `5.3`
- Main content folder: `Content/MedievalPaintings7`
- Demo map: `Content/MedievalPaintings7/Maps/Demo.umap`

The pipeline rewrites the generated project's `.uproject` to `EngineAssociation` `5.0` and renames the content folder to the current pack folder name. UE 5.0.3 must then open and resave the project assets to validate compatibility.

