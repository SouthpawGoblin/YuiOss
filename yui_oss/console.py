# -*- coding: utf-8 -*-

import argparse
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
        self.methods = ("cd", "ls")

        self.parser = ArgumentParser(description="YuiOss console application ver " + VERSION)
        self.parser.add_argument("-a", "--all", action="store_true")
        self.parser.add_argument("-r", "--recursive", action="store_true")
        self.parser.add_argument("method", choices=self.methods, nargs=1)
        self.parser.add_argument("args", nargs=argparse.ZERO_OR_MORE)

    def run(self):
        self.args = self.parser.parse_args()
        method = self.args.method[0]
        if method in self.methods:
            self.__getattribute__(method)()

    def update_attr(self):
        with open(self.ATTR_FILE, 'w+') as f:
            yaml.dump(self.attrs, f)

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
                raise YuiConsoleException("cd path should be a directory")
            path = self.fm.norm_path(path)
            self.root = path[1:] if path.startswith(self.fm.SEP) else self.root + path
        self.attrs["root"] = self.root
        self.update_attr()
        print("current directory changed to: /" + self.root)

    def ls(self):
        """
        list sub directories and files of current directory
        :return:
        """
        files = [obj.key for obj in self.fm.list_dir(self.root, self.args.all)]
        print("listing: /" + self.root + '\n' + '\t'.join(files) if len(files)
              else "current directory: /" + self.root + " is empty.")


