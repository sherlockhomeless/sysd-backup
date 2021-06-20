#!/usr/bin/env python3

import tarfile
from cryptography.fernet import Fernet

import argparse
import os
import sys
import shutil

"""
tutorials:
    * encryption: https://www.geeksforgeeks.org/encrypt-and-decrypt-files-using-python/
    * zipping: https://thispointer.com/python-how-to-create-a-zip-archive-from-multiple-files-or-directory/,

todo: config/env integration for parameter to not have to change unit-files if path changes
"""


def main():
    args = parse_arguments()
    print(args)
    if args.backup != '':
        backup(args)
    if args.restore != '':
        restore(args)
    elif args.generate_key:
        generate_key()


def backup(args: argparse.Namespace):
    def zip_folder(path: str) -> str:
        """
        creates a zip file from the directory given
        :param path: path to file/directory to zip
        :return: path to the created zip file
        """
        tar_file: str = f'/tmp/{path.split("/")[-1]}.tar.gz'
        basedir: str = os.path.dirname(path)
        file_name: str = os.path.basename(path)
        original_dir: str = os.getcwd()
        os.chdir(basedir)
        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(file_name)
        print(f"[BACKUP]: created zip-archive at {tar_file}")
        os.chdir(original_dir)
        return tar_file

    def encrypt_file(path_file: str, path_key: str) -> str:
        """
        :param path_file: file to encrypt
        :param path_key: path to symmetric key
        :return: path to encrypted file
        """
        encrypted_file_name: str = '/tmp/' + path_file.split('/')[-1] + ".save"
        with open(path_key, 'rb') as keyfile:
            key = keyfile.read()
        fernet: Fernet = Fernet(key)
        with open(path_file, 'rb') as file:
            org = file.read()
        encrypted = fernet.encrypt(org)
        with open(encrypted_file_name, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        print(f"[ENCRYPT]: wrote encrypted file to {encrypted_file_name}")
        return encrypted_file_name

    def move_file_to_backup_location(path_file: str, path_backup: str):
        shutil.move(path_file, os.path.join(path_backup, os.path.basename(path_file)))
        print(f"[MOVE]: moved file from {path_file} to {path_backup}")

    (backup_src, backup_target) = args.backup.split(':')
    key_path: str = args.key
    zip_folder_path: str = zip_folder(backup_src)
    encrypt_file_path: str = encrypt_file(zip_folder_path, key_path)
    move_file_to_backup_location(encrypt_file_path, backup_target)
    print("[COMPLETE]: backup completed")


def restore(args: argparse.Namespace):
    def unzip_folder(zip_path: str, zip_target: str):
        tar = tarfile.open(zip_path)
        os.chdir(zip_target)
        tar.extractall()
        print(f"[UNZIP] unzipping {zip_path} to {zip_target}")

    def decrypt_file(file_path: str, key_path: str) -> str:
        decrypted_zip_path = '/tmp/sysd-backup.zip'
        with open(file_path, 'rb') as enc_file:
            encrypted = enc_file.read()
        with open(key_path, 'rb') as keyfile:
            key = keyfile.read()
        fernet: Fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted)
        with open(decrypted_zip_path, 'wb') as dec_file:
            dec_file.write(decrypted)
        print(f"[DECRYPT] decrypted {file_path} with key at {key_path}")
        return decrypted_zip_path

    (restore_src, restore_target) = args.restore.split(':')
    print(f"[RESTORE] restoring {restore_src} into {restore_target}")
    key_path: str = args.key
    decrypted_zip = decrypt_file(restore_src, key_path)
    unzip_folder(decrypted_zip, restore_target)


def generate_key():
    """
    Generates a fernet key;
    """
    # key generation
    key_name = 'filekey.key'
    key = Fernet.generate_key()

    # string the key in a file
    with open(key_name, 'wb') as filekey:
        filekey.write(key)

    print(f"[KEY_GEN]: saved new keyfile with name {key_name}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='simple, robust and encrypting backup tool')
    parser.add_argument('--backup', metavar='backup-src:backup-dest', type=str, nargs='?', default='', help='source-path:target-path' )
    parser.add_argument('--restore', metavar='backup-path:restore-dest', type=str, nargs='?', default='', help='backup-path:restore-path' )
    parser.add_argument('--key', metavar='key', type=str, nargs='?', help='path to symmetrical key')
    parser.add_argument('--generate-key',  action='store', nargs='?', help='generates a symmetric key at cwd')
    args = parser.parse_args()

    if args.backup != '' or args.restore != '':
        try:
            assert ':' in args.backup or ':' in args.restore
            assert os.path.exists(args.backup.split(':')[0]) or os.path.exists(args.restore.split(':')[0])
            assert args.key is not None
        except AssertionError:
            print("[ERROR]: problem with parameters for backup/restore", file=sys.stderr)
            sys.exit(1)

    return args


if __name__ == '__main__':
    main()
