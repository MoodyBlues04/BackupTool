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
    GIT_BACKUP = 'git_backup_src_file'
    
    REQUIRED = {DOCUMENT_ROOT, BACKUP_SRC, BACKUP_DESC, DB_BACKUP, GIT_BACKUP}
    
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
    
    def execute(self) -> None:
        res = exec_shell_command(self.__backup_command())
        report(res)
    
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
    SQLITE = 'sqlite3'
    
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
            self.MONGODB: self.__backup_mongodb,
            self.POSTGRES: self.__backup_postgres,
            self.SQLITE: self.__backup_sqlite,
        }
        return handlers[connection_type]
    
    def __backup_mysql(self, db_conf: dict) -> subprocess.CompletedProcess:
        password_s = ''
        if db_conf['password']:
            password_s = '-p' + db_conf['password']
        desc_file = self.__desc_sql_dump('sql')
        
        command = f"mysqldump -u{db_conf['username']} {password_s} {db_conf['database']} > {desc_file}"
        
        return exec_shell_command(command)
    
    def __backup_postgres(self, db_conf: dict) -> subprocess.CompletedProcess:
        password_s = ''
        if db_conf['password']:
            password_s = f"PGPASSWORD='{db_conf['password']}'"
        desc_file = self.__desc_sql_dump('pgsql')
        
        command = f"{password_s} pg_dump -U {db_conf['username']} -h {db_conf['host']} {db_conf['database']} > {desc_file}"
        
        return exec_shell_command(command)
    
    def __backup_mongodb(self, db_conf: dict) -> subprocess.CompletedProcess:
        auth_s = ''
        if db_conf.get('auth_table'):
            auth_s = f"--authenticationDatabase='{db_conf['auth_table']}' -u='{db_conf['username']}' -p='{db_conf['password']}'"
        desc_dir =  self.__config.get(Config.BACKUP_DESC) + '/mongodb'
        
        command = f"mongodump --host={db_conf['host']} --port={db_conf['port']} {auth_s} -o '{desc_dir}'"
        
        return exec_shell_command(command)
    
    def __backup_sqlite(self, db_conf: dict) -> subprocess.CompletedProcess:
        desc_file = self.__desc_sql_dump('sq3') + '.bak'
        command = f"sqlite3 {db_conf['path']} '.backup {desc_file}'"
    
        return exec_shell_command(command)
    
    def __desc_sql_dump(self, type: str) -> str:
        return self.__config.get(Config.BACKUP_DESC) + f'/{type}-dump.{type}'


class GitBackup:
    def __init__(self, config: Config) -> None:
        self.__config = config
    
    def execute(self) -> None:
        if not self.__config.get(Config.GIT_BACKUP):
            return
        
        source_filename = self.__config(Config.GIT_BACKUP)
        with open(source_filename) as source_file:
            project_list = source_file.readlines()
            print(project_list)
        
        for project_root in project_list:
            command = f"cd {project_root} && git add . && git commit -m \"backup auto-commit\" && git push"
            res = exec_shell_command(command)
            report(res)


def main():
    config = Config()
    config.make_today_desc_dir()
    
    FileBackup(config).execute()
    DbBackup(config).execute()
    GitBackup(config).execute()
    

if __name__ == '__main__':
    main()