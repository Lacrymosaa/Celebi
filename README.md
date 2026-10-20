# Celebi - Auto Save Backup

Celebi is a lightweight, portable Windows application that runs quietly in your system tray and automatically backs up your game save files every time they are updated. It helps prevent corrupted saves and ruined runs by allowing you to easily "time travel" to a previous game state.

## Features
* **Automatic Backups:** Detects when the game updates a save file and creates a timestamped backup folder.
* **Storage Management:** Keeps only the 5 most recent backups, automatically deleting older ones to save disk space.
* **System Tray Integration:** Runs invisibly in the background while you play.
* **One-Click Restore:** Features a simple UI to select an old backup and overwrite the current game save.

## How to Use
1. Download the latest `.exe` file from the [Releases](../../releases) page.
2. Run the executable. It will minimize directly to your system tray (next to the Windows clock).
3. Right-click the Celebi icon to open the interface or to quit the application.
4. Play your game! Your backups will be stored safely in your `AppData\Local` folder.

## How to Configure for Other Games
If you are a developer and want to compile this tool for a different game, you only need to change two small things in the `main.py` source code before compiling.

**1. Change the Save Folder Location**
Find the `self.game_dir` variable inside the `__init__` function and change it to the target game's save path:
```python
# Example for a different game folder
self.game_dir = os.path.join(self.local_appdata, 'YourGameName', 'Saves')

```

**2. Change the Tracked Files**
Find the `get_save_files(self)` function and update the list of the exact file names you want the script to monitor:

```python
# Update the list with the target game's specific save file names
arquivos_exatos = ['save1.dat', 'profile.sav', 'auto_save.bin']

```

After making these changes, recompile the script using PyInstaller.

```

```