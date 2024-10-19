import os
from os.path import isfile
from pathlib import Path
from typing import List
from syftbox.lib import Client, SyftPermission
from types import SimpleNamespace
import json


def setup_folder(client_config: Client, folder: Path) -> None:
    print("Setting up the necessary folders.")
    folder.mkdir(parents=True, exist_ok=True)

    # after this there will be files (so we can sync)
    permission = SyftPermission.mine_with_public_write(client_config.email)
    permission.ensure(folder)


if __name__ == "__main__":
    
    
    client = Client.load()
    # this is where all the app state goes
    ring_pipeline_path: Path = (
        Path(client.datasite_path) / "app_pipelines" / "fl_ring"
    )
    observer_pipeline_path: Path = (
        Path(client.datasite_path) / "app_pipelines" / "ring_observer"
    )
    if not observer_pipeline_path.is_dir():
        setup_folder(client, observer_pipeline_path)

    running_folder: Path = ring_pipeline_path / "running"

    file_path = Path(running_folder / "data.json")
    if file_path.is_file():
        try:
            with open(str(file_path), 'r') as f:
                data_json = json.load(f)
                observer_path = data_json.get('observer', None)
                if observer_path is not None:
                    observer_file_path = Path(client.datasite_path).parent / Path(observer_path + "/data.json") 
                    if observer_file_path.is_file():
                        with open(str(observer_file_path),  'r+') as json_file:
                            old_info = json.load(json_file)
                            if old_info['current_index'] < data_json['current_index']:
                                json_file.seek(0)
                                json.dump(data_json, json_file, indent=4)
                                json_file.truncate()
                            else:
                                print("Old info is up to date, no need to update the file.")
                    else:
                        with open(str(observer_file_path),  'w') as json_file:
                            json.dump(data_json, json_file, indent=4)

        except Exception as e:
            print("\n\n\n\n\nCouldn't read it \n\n\n", e)
    else:
        print("\n\n\n File doesn't exist, skipping...\n\n\n")
