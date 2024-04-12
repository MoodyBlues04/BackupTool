# Backup tool for linux projects

## Requirements
+ linux tools: rsync
+ python >= 3
  
## Usage

1. fill config.json:
   1. document_root - pwd to project root
   2. backup_desc - relative path to backup folder (default it is backup folder in root of project)
   3. backup_src_file - file with list of folders for backup
2. fill file with dir list to backup (from punctum 1.3)
3. 