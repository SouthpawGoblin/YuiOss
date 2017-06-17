# -*- coding: utf-8 -*-
"""
YuiSync exceptions
"""


class YuiException(Exception):
    """
    base exception for all custom exceptions
    """
    pass


class YuiBucketException(YuiException):
    """
    base exception raised when error occurs while operating buckets
    """
    pass


class YuiFileException(YuiException):
    """
    base exception raised when error occurs while operating files
    """
    pass


class YuiListBucketException(YuiBucketException):
    """
    raised when error occurs while listing buckets
    """
    pass


class YuiChangeBucketException(YuiBucketException):
    """
    raised when error occurs while changing buckets
    """
    pass


class YuiCreateBucketException(YuiBucketException):
    """
    raised when error occurs while creating bucket
    """
    pass


class YuiDeleteBucketException(YuiBucketException):
    """
    raised when error occurs while deleting bucket
    """
    pass


class YuiIsExistException(YuiFileException):
    """
    raised when error occurs while checking file's existence
    """
    pass


class YuiGetMD5Exception(YuiFileException):
    """
    raised when error occurs while getting file MD5
    """
    pass


class YuiUploadException(YuiFileException):
    """
    raised when error occurs while uploading files
    """
    pass


class YuiDownloadException(YuiFileException):
    """
    raised when error occurs while downloading files
    """
    pass


class YuiDeleteException(YuiFileException):
    """
    raised when error occurs while deleting files
    """
    pass


class YuiCopyException(YuiFileException):
    """
    raised when error occurs while copying files
    """
    pass


class YuiMoveException(YuiFileException):
    """
    raised when error occurs while moving/renaming files
    """
    pass


class YuiListDirException(YuiFileException):
    """
    raised when error occurs while listing files
    """
    pass
