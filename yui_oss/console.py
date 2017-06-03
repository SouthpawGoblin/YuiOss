# -*- coding: utf-8 -*-

import argparse
from colorama import init, Fore
from argparse import ArgumentParser
from .manager import OssFileManager, VERSION
from .exception import *
import yaml
import itertools


class Yui:

    ATTR_FILE = ".yui"

    def __init__(self, config_file_path):
        with open(config_file_path, 'r') as f:
            self.config = yaml.load(f)
            self.fm = OssFileManager(self.config["auth_key"],
                                     self.config["auth_key_secret"],
                                     self.config["endpoint"],
                                     self.config["bucket_name"],
                                     proxies=self.config["proxies"])

        try:
            with open(self.ATTR_FILE, 'r') as f:
                self.attrs = yaml.load(f)
                self.root = self.attrs["root"] if self.attrs and self.attrs["root"] else ""
        except FileNotFoundError:
            with open(self.ATTR_FILE, "w") as f:
                self.attrs = {"root": ""}
                yaml.dump(self.attrs, f)
                self.root = ""

        self.args = None
        self.methods = ("cd", "ls", "ul", "dl", "cp")

        self.parser = ArgumentParser(description="YuiOss console application ver " + VERSION)
        self.parser.set_defaults(verbose=True)
        self.parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
        self.parser.add_argument("-q", "--quiet", dest="verbose", action="store_false")
        self.parser.add_argument("-a", "--all", action="store_true")
        self.parser.add_argument("-r", "--recursive", action="store_true")
        self.parser.add_argument("method", choices=self.methods, nargs=1)
        self.parser.add_argument("args", nargs=argparse.ZERO_OR_MORE)

        init()

    def run(self):
        self.args = self.parser.parse_args()
        method = self.args.method[0]
        if method in self.methods:
            self.__getattribute__(method)()

    def update_attr(self):
        with open(self.ATTR_FILE, 'w+') as f:
            yaml.dump(self.attrs, f)

    def on_success(self, method, src, dest, result):
        if self.args.verbose:
            print(Fore.GREEN + str(method) + " success: " +
                  src + ("" if not dest else " --> " + dest))

    def on_error(self, method, src, dest, result):
        print(Fore.RED + str(method) + " success: " +
              src + ("" if not dest else " --> " + dest))

    def cd(self):
        """
        change oss current directory
        :param path: new current directory, will be considered as absolute path if starts with '/'
        :return:
        """
        if not len(self.args.args):
            self.root = ""
        else:
            path = self.args.args[0]
            if not self.fm.is_dir(path):
                print(Fore.RED + "cd path should be a directory")
                return
            path = self.fm.norm_path(path)
            self.root = path[1:] if path.startswith(self.fm.SEP) else self.root + path
        self.attrs["root"] = self.root
        self.update_attr()
        print(Fore.GREEN + "current directory changed to: /" + self.root)

    def ls(self):
        """
        list sub directories and files of current directory
        :return:
        """
        files = [obj.key for obj in self.fm.list_dir(self.root, self.args.all)]
        print((Fore.GREEN + "listing: /" + self.root + '\n' + '\t'.join(files)) if len(files)
              else (Fore.YELLOW + "current directory: /" + self.root + " is empty."))

    def ul(self):
        """
        upload
        :return:
        """
        if len(self.args.args) != 2:
            print(Fore.RED + "'ul' needs 2 input arguments: src, dest")
            return
        src = self.args.args[0]
        dest = self.args.args[1][1:] if self.args.args[1].startswith(self.fm.SEP) else self.root + self.args.args[1]
        try:
            self.fm.upload(src, dest,
                           recursive=self.args.recursive,
                           on_success=self.on_success, on_error=self.on_error)
        except YuiException as e:
            print(Fore.RED + "'ul' encountered an error: \n" +
                  str(e))

    def dl(self):
        """
        download
        :return:
        """
        if len(self.args.args) != 2:
            print(Fore.RED + "'dl' needs 2 input arguments: src, dest")
            return
        src = self.args.args[0][1:] if self.args.args[0].startswith(self.fm.SEP) else self.root + self.args.args[0]
        dest = self.args.args[1]
        try:
            self.fm.download(src, dest,
                             recursive=self.args.recursive,
                             on_success=self.on_success, on_error=self.on_error)
        except YuiException as e:
            print(Fore.RED + "'dl' encountered an error: \n" +
                  str(e))

    def cp(self):
        """
        copy, recursive by default
        :return:
        """
        if len(self.args.args) != 2:
            print(Fore.RED + "'cp' needs 2 input arguments: src, dest")
            return
        src = self.args.args[0][1:] if self.args.args[0].startswith(self.fm.SEP) else self.root + self.args.args[0]
        dest = self.args.args[1][1:] if self.args.args[1].startswith(self.fm.SEP) else self.root + self.args.args[1]
        try:
            self.fm.copy(src, dest,
                         on_success=self.on_success, on_error=self.on_error)
        except YuiException as e:
            print(Fore.RED + "'cp' encountered an error: \n" +
                  str(e))
