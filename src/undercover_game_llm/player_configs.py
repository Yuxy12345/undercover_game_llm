import os.path

import toml

def load_player_configs(toml_path):
    data = toml.load(toml_path)
    return data['player']


player_configs = load_player_configs('conf/player_config.toml')