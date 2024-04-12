import subprocess
import json
from datetime import date
from pathlib import Path


def exec_shell_command(command: str|list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE)

def report(subprocess: subprocess.CompletedProcess) -> None:
    print(f"Subprocess completed. Args: {subprocess.args}, code: {subprocess.returncode}, stdout: {subprocess.stdout}")


class Config:
    DOCUMENT_ROOT = 'document_root'
    BACKUP_SRC = 'backup_src_file'
    BACKUP_DESC = 'backup_desc'
    DB_BACKUP = 'database_backup'
    
    REQUIRED = {DOCUMENT_ROOT, BACKUP_SRC, BACKUP_DESC, DB_BACKUP}
    
    def __init__(self) -> None:
        config_file = open('config.json')
        self.__config: dict = json.load(config_file)
        self.__validate()
    
    def get(self, key: str, default = None) -> str:
        return self.__config.get(key, default)
    
    def make_today_desc_dir(self) -> None:
        desc_dir = self.get(self.BACKUP_DESC)
        today_desc = f"{desc_dir}/{date.today().strftime('%d-%m-%Y')}"
        Path(today_desc).mkdir(parents=True, exist_ok=True)
        self.__config[self.BACKUP_DESC] = today_desc
    
    def __validate(self) -> None:
        config_keys = self.__config.keys()
        for key in self.REQUIRED:
            if key not in config_keys:
                raise Exception(f'Fill key `{key}` in config.json')


class FileBackup:
    def __init__(self, config: Config) -> None:
        self.__config = config
    
    def execute(self) -> subprocess.CompletedProcess:
        return exec_shell_command(self.__backup_command())
    
    def __backup_command(self) -> str:
        return 'rsync ${DEBUG:+-nv} -arR --files-from=%s %s %s' % (
            self.__config.get(Config.BACKUP_SRC),
            self.__config.get(Config.DOCUMENT_ROOT),
            self.__config.get(Config.BACKUP_DESC)
        )


class DbBackup:
    MYSQL = 'mysql'
    MONGODB = 'mongodb'
    POSTGRES = 'postgres'
    SQLITE = 'sqlite'
    
    CONNECTION_TYPES = {MYSQL, MONGODB, POSTGRES, SQLITE}
    
    def __init__(self, config: Config) -> None:
        self.__config = config
    
    def execute(self) -> subprocess.CompletedProcess:
        for db_conf in self.__config.get(Config.DB_BACKUP):
            connection_type = db_conf.get('connection')
            if connection_type not in self.CONNECTION_TYPES:
                raise Exception(f'Invalid connection type: `{connection_type}`')
            
            handler = self.__get_backup_handler(connection_type)
            report(handler(db_conf))
    
    def __get_backup_handler(self, connection_type: str):
        handlers = {
            self.MYSQL: self.__backup_mysql,
            self.MONGODB: lambda el: print(el),
            self.POSTGRES: lambda el: print(el),
            self.SQLITE: lambda el: print(el),
        }
        return handlers[connection_type]
    
    def __backup_mysql(self, db_conf: dict) -> subprocess.CompletedProcess:
        command = 'mysqldump -u%s –p%s %s > %s' % (
            db_conf['username'],
            db_conf['password'],
            db_conf['database'],
            self.__config.get(Config.BACKUP_DESC) + '/mysql-dump.sql'
        )
        return exec_shell_command(command)


def main():
    config = Config()
    config.make_today_desc_dir()
    
    result = FileBackup(config).execute()
    report(result)
    
    DbBackup(config).execute()
    

if __name__ == '__main__':
    main()