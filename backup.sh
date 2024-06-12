#!/bin/bash

while getopts b:r: flag
do
  case "${flag}" in
    b) 
    # OPTARG = nothing - pass anything
    # BACKUP
    # echo "Importing .env file"
    cd $OPTARG
    export $(grep -v '^#' dev.env | xargs -d '\n')
    BACKUP_DIR=backups/$(date +'%Y/%m/%d/%H_%M_%S')
    echo "Backuping to ${BACKUP_DIR}..."
    mkdir -p $BACKUP_DIR
    # chown -R hes:hes ./$BACKUP_DIR
    docker exec db pg_dump -U $POSTGRES_USER -d $POSTGRES_DB -a -f /usr/src/web/$BACKUP_DIR/db.dump --column-inserts
    echo "Backuped db - DONE"
    # tar -cf $BACKUP_DIR/data.tar ./media/boxUZI ./media/originalUZI ./media/segUZI
    tar -cvf ${OPTARG}/$BACKUP_DIR/data.tar ./media/boxUZI ./media/originalUZI ./media/segUZI
    echo "Backuped data - DONE"
    ;;
    r) 
    # OPTARG = path to directory with backups withoup backups root (ex. 2023/02/01/19_55_32)
    echo "Restoring..."
    docker exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -f /usr/src/web/backups/${OPTARG}/db.dump
    tar -xvf backups/${OPTARG}/data.tar
    echo "Database restore - DONE"
    ;;
  esac
done
