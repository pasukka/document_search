import yaml


class Config:
    llm: str

    def __init__(self, llm: str, docs_path: str):
        self.llm = llm
        self.docs_path = docs_path


def load_config(file_path: str) -> Config:
    with open(file_path, 'r', encoding='utf-8') as stream:
        config_dict = yaml.safe_load(stream)['app-config']

    return Config(config_dict['llm'], 
                  config_dict['docs_path'])
