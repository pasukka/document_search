import yaml


class Config:
    llm: str
    docs_path: str
    debug_mode: bool

    def __init__(self, llm: str, docs_path: str, debug_mode: bool):
        self.llm = llm
        self.docs_path = docs_path
        self.debug_mode = debug_mode


def load_config(file_path: str) -> Config:
    with open(file_path, 'r', encoding='utf-8') as stream:
        config_dict = yaml.safe_load(stream)['app-config']

    return Config(config_dict['llm'],
                  config_dict['docs_path'],
                  config_dict['debug_mode'])
