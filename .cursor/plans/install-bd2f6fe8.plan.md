<!-- bd2f6fe8-056b-4562-b3d8-0a34109a5714 2bafd1f2-9bfa-4286-b5c2-9c24b72950af -->
# Install & Run Plan for HyprRice

#### Overview
We will install HyprRice in your venv, reconcile packaging (entry points/data files), fix runtime issues (CLI migration, main imports/deps usage, Hyprland utils), and adjust GUI startup (history/backup managers, plugin sandbox defaults, error handler). Then we’ll run tests and the CLI/GUI.

#### Steps
1) Environment setup
- Use the existing venv at `venv/`. Upgrade pip and install dev/test deps.
- Install HyprRice in editable mode with pyproject metadata.

2) Packaging and entry points
- Make `hyprrice` CLI point to `hyprrice.cli:main` (consistent with `pyproject.toml`).
- Update `setup.py` entry_points to `hyprrice.cli:main` and remove missing `data_files`/`package_data` entries that reference non-existent assets.

3) Core runtime fixes
- Fix `src/hyprrice/utils.py` `hyprctl()` to return `(returncode, stdout, stderr)` and do not force `-j` (provide a `json` flag). Update `hyprctl_async` similarly.
- Ensure `animations.py` and other call sites work with the new `hyprctl` signature (they already expect a tuple, so this resolves the mismatch).
- Add `import os` at the top of `src/hyprrice/main.py` (used in `check_system_requirements`).
- In `main.py`, treat `check_dependencies()` result as a dict; determine success by counting required-missing entries instead of using it as a boolean.

4) CLI migration command
- In `src/hyprrice/cli.py`, update `cmd_migrate()` to use the actual migration API: call `migrate_user_config(...)` (from `migration.py`) and emit success/backup info without expecting a dict.

5) GUI startup hardening
- In `src/hyprrice/main_gui.py`:
  - Construct `HistoryManager(config)` (okay) and `BackupManager(config.paths.backup_dir)` instead of passing `config`.
  - Use `getattr(self.config.gui, 'debug_mode', False)` in the global error handler to avoid referencing a non-existent field.
  - Default `enable_sandbox=False` for plugins by default (sandbox currently expects plugin directories, while repo ships file-based plugins). Keep a pathway to enable later from Preferences.

6) Optional minor cleanups (fast wins)
- In `cli.py`, make `doctor` and `check` present dependency results consistently (they already do; no functional change required).
- Ensure ThemeManager path resolution is absolute-safe: resolve `themes` dir via `Path(__file__).resolve().parents[2] / 'themes'`.

7) Install and test
- Run `pytest -q` and fix quick failures (if any) that stem from the above changes (e.g., import errors, signature mismatches).
- Run `hyprrice doctor` and verify graceful behavior if Hyprland is not running.
- Launch `hyprrice gui` to ensure the window appears without plugin crashes.

8) Commit
- Commit the edits with a clear message and brief changelog update.

#### Key Edits (essential snippets)
- hypr