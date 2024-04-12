# Backup tool for linux projects

## Requirements
+ linux tools: rsync
+ python >= 3Ba
+ mysql, postgres, mongodb, sqlite3 extensions if you want to backup each type of database
  
## Usage

1. File backup
    Fill ```config.json```:
      + document_root - pwd to project root
      + backup_desc - relative path to backup folder (default it is backup folder in root of project)
      + backup_src_file - file with list of folders for backup
    Fill file with dir list to backup (from punctum 1.3)
2. Db backup
   Fill ```config.json``` ```database_backup``` field with data as specified in its example

When ```config.json``` is fully set up, just run ```python3 backup.py``` to backup all project,
your files and databases will be stored in ```/<chosen_dir>/<current_date>``` directory