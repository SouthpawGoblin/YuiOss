# -*- coding: utf-8 -*-
"""
YuiSync exceptions
"""


class YuiException(Exception):
    """
    base exception for all custom exceptions
    """
    pass


class YuiUploadException(YuiException):
    """
    raised when error occurred while uploading files
    """
    pass


class YuiDownloadException(YuiException):
    """
    raised when error occurred while downloading files
    """
    pass


class YuiDeleteException(YuiException):
    """
    raised when error occurred while deleting files
    """
    pass


class YuiCopyException(YuiException):
    """
    raised when error occurred while copying files
    """
    pass


class YuiMoveException(YuiException):
    """
    raised when error occurred while moving/renaming files
    """
    pass


class YuiListDirException(YuiException):
    """
    raised when error occurred while listing files
    """
    pass
