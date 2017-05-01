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
    raised when error occurred while uploading files
    """
    pass


class YuiDeleteException(YuiException):
    """
    raised when error occurred while uploading files
    """
    pass


class YuiMoveException(YuiException):
    """
    raised when error occurred while uploading files
    """
    pass
