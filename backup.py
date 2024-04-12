import subprocess
import json

def get_config() -> dict:
    with open('congig.json') as config_file:
        return json.load(config_file)


def main():
    config = get_config()
    
    command = 'rsync ${DEBUG:+-nv} -arR --files-from=%s %s %s' % (
        config['backup_src_file'],
        config['document_root'],
        config['backup_dest']
    )
    print(command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    print(result.stdout)
    print(result.returncode)


if __name__ == '__main__':
    main()