# -*- coding: utf-8 -*-

from optparse import OptionParser
import yui_oss as yui
import yaml

VERSION = yui.__version__


def main():
    parser = OptionParser(usage="usage: %prog [options] arg", version="%prog " + VERSION)
    f = open("../config.yaml")
    config = yaml.load(f)
    fm = yui.OssFileManager(config["auth_key"],
                            config["auth_key_secret"],
                            config["endpoint"],
                            config["bucket_name"],
                            config["proxies"])

    parser.set_defaults(verbose=True,
                        wave_msg="Hello Starter!")

    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose",
                      help="don't print status messages to stdout")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      help="print status messages to stdout")
    parser.add_option("-w", "--wave",
                      action="store", dest="wave_msg",
                      help="sample option")

    (options, args) = parser.parse_args()
    if len(args):
        parser.error("argument(s) <{0}> is(are) not valid".format(' '.join([arg for arg in args])))
    if options.verbose:
        print(options.wave_msg)

if __name__ == "__main__":
    main()

