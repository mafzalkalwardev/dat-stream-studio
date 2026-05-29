# DAT Stream Studio Companion

Clean Manifest V3 companion extension.

It keeps a few useful ideas from the analyzed DatEx extension:

- browser popup
- saved shortcuts
- local storage
- explicit cookie count / clear action

It intentionally does not do cookie synchronization, GitHub token storage, remote Pastebin loading, or shared DAT session import.

## Load In Chrome

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Click **Load unpacked**.
4. Select this `dat_companion_extension` folder.

## Permissions

The extension asks for `cookies`, `tabs`, and `storage`, plus DAT host permissions. It uses these only for local DAT cookie count/clear and opening shortcuts.
