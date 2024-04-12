# Backup tool for linux projects

## Requirements
+ linux tools: rsync
+ python >= 3
  
## Usage

1. File backup
    Fill ```config.json```:
      + document_root - pwd to project root
      + backup_desc - relative path to backup folder (default it is backup folder in root of project)
      + backup_src_file - file with list of folders for backup
    Fill file with dir list to backup (from punctum 1.3)
2. Db backup
   Fill ```config.json``` ```database_backup``` field with data as specified in its example