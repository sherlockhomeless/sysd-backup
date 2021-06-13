#!/usr/bin/env python3
from zipfile import ZipFile
from os.path import basename
from cryptography.fernet import Fernet
from time import strftime,localtime

import argparse
import os
import sys

"""
todo: config-file
"""


def main():
    args = parse_arguments()
    print(args)
    if args.backup != '':
        backup(args)
    elif args.generate_key:
        generate_key()


def backup(args: argparse.Namespace):
    def zip_folder(path: str) -> str:
        """
        creates a zip file from the directory given
        :param path: path to file/directory to zip
        :return: path to the created zip file
        """
        path_zip_file: str = f'/tmp/{path.split("/")[-1]}' + strftime("_%Y_%m_%d-%H:%M", localtime()) + '.zip'
        zip_obj: ZipFile = ZipFile(path_zip_file, 'w')
        for folderName, subfolders, filenames in os.walk(path):
            for filename in filenames:
                # create complete filepath of file in directory
                file_path = os.path.join(folderName, filename)
                # Add file to zip
                zip_obj.write(file_path, basename(file_path))
        zip_obj.close()
        print(f"[BACKUP]: created zip-archive at {path_zip_file}")
        return path_zip_file

    def encrypt_file(path_file: str, path_key: str) -> str:
        """
        src: https://www.geeksforgeeks.org/encrypt-and-decrypt-files-using-python/
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

    (backup_src, backup_target) = args.backup.split(':')
    key_path: str = args.key
    zip_folder_path: str = zip_folder(backup_src)
    encrypt_file_path: str = encrypt_file(zip_folder_path, key_path)



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
    parser.add_argument('--key', metavar='key', type=str, nargs='?', help='path to symmetrical key')
    parser.add_argument('--generate-key',  action='store', nargs='?', help='generates a symmetric key at cwd')
    args = parser.parse_args()

    if args.backup != '':
        try:
            assert ':' in args.backup
            assert os.path.exists(args.backup.split(':')[0])
            assert args.key is not None
        except AssertionError:
            print("[ERROR]: problem with parameters for backup", file=sys.stderr)
            sys.exit(1)

    return args


if __name__ == '__main__':
    main()
