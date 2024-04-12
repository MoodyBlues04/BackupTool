import subprocess
import json

class Config:
    DOCUMENT_ROOT = 'document_root'
    BACKUP_SRC = 'backup_src_file'
    BACKUP_DESC = 'backup_desc'
    
    REQUIRED = {DOCUMENT_ROOT, BACKUP_SRC, BACKUP_DESC}
    
    def __init__(self) -> None:
        config_file = open('config.json')
        self.__config: dict = json.load(config_file)
        self.__validate()
    
    def get(self, key: str, default = None) -> str:
        return self.__config.get(key, default)
    
    def __validate(self) -> None:
        config_keys = self.__config.keys()
        for key in self.REQUIRED:
            if key not in config_keys:
                raise Exception(f'Fill key `{key}` in config.json')


class Rsync:
    def __init__(self, config: Config) -> None:
        self.__config = config
    
    def execute(self) -> subprocess.CompletedProcess:
        return subprocess.run(self.__backup_command(), shell=True, stdout=subprocess.PIPE)
    
    def __backup_command(self) -> str:
        return 'rsync ${DEBUG:+-nv} -arR --files-from=%s %s %s' % (
            self.__config.get(Config.BACKUP_SRC),
            self.__config.get(Config.DOCUMENT_ROOT),
            self.__config.get(Config.BACKUP_DESC)
        )


def main():
    config = Config()
    
    result = Rsync(config).execute()
    print(result.stdout)
    print(result.returncode)


if __name__ == '__main__':
    main()