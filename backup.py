import subprocess


def main():
    command = 'rsync ${DEBUG:+-nv} -arR --files-from=./dir-list.txt /var/www/BackupTool/ ./test-desc/'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    print(result.stdout)
    print(result.returncode)


if __name__ == '__main__':
    main()