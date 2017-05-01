"""
class for manipulating objects
"""
from . import utils
from .exception import *
import oss2
import os
import binascii
import base64
import re


class OssFileManager:
    """
    class for managing oss files
    """

    # since bucket.upload() may get 407 when content is empty,
    # I give all directory objects "$DIR$" as content
    LOCAL_DIR_CONTENT = "$DIR$"
    # MD5 of DIR_CONTENT, local folders will get this MD5 as etag, but md5 of a dir will never be used
    LOCAL_DIR_CONTENT_MD5 = utils.content_md5(LOCAL_DIR_CONTENT)

    MD5_HEADER_STRING = 'Content-MD5'

    def __init__(self, auth_key, auth_key_secret, endpoint, bucket_name):
        auth = oss2.Auth(auth_key, auth_key_secret)
        self.__bucket = oss2.Bucket(auth, endpoint, bucket_name, enable_crc=False)

    def get_md5(self, remote):
        """
        try get file md5 from header 'Content-MD5',
        if failed return etag
        :param remote: abs oss path, directory should end with '/'
        :return: md5 string
        """
        try:
            remote = OssFileManager.norm_path(remote)
            head = self.__bucket.head_object(remote)
            if OssFileManager.MD5_HEADER_STRING in head.headers:
                return OssFileManager.base64_to_md5(head.headers[OssFileManager.MD5_HEADER_STRING])
            else:
                return head.etag
        except Exception as e:
            raise YuiException(e)

    def is_exist(self, remote):
        """
        wrapper for Bucket.object_exists()
        :param remote: abs oss path, directory should end with '/'
        :return: boolean
        """
        try:
            remote = OssFileManager.norm_path(remote)
            return self.__bucket.object_exists(remote)
        except Exception as e:
            raise YuiException(e)

    def upload(self, local, remote, recursive=False, on_success=None, on_error=None, progress_callback=None):
        """
        upload a file/directory to OSS
        if `local` is a directory and `recursive` set to True, all contents will be uploaded recursively
        if http status of upload result >= 400, `on_error` callback will be called, else `on_success` will be called
        `local`, `remote` and upload result object will be passed to callback methods
        :param local: local source path
        :param remote: abs oss path, directory should end with '/'
        :param recursive: boolean
        :param on_success: success callback
        :param on_error: error callback
        :param progress_callback:
        :return: class:`PutObjectResult <oss2.models.PutObjectResult>`
        """
        # TODO: resumable support
        # TODO: multipart support
        try:
            local = os.path.abspath(local)
            remote = OssFileManager.norm_path(remote)
            if os.path.isdir(local):
                if OssFileManager.is_dir(remote):
                    dest_remote = remote + os.path.split(local)[-1] + '/'
                else:
                    raise Exception("remote path should be a directory")
                md5 = OssFileManager.LOCAL_DIR_CONTENT_MD5
                md5_b64 = OssFileManager.md5_to_base64(md5)
                result = self.__bucket.put_object(dest_remote, OssFileManager.LOCAL_DIR_CONTENT,
                                                  headers={OssFileManager.MD5_HEADER_STRING: md5_b64},
                                                  progress_callback=progress_callback)
                if recursive:
                    for subdir in os.listdir(local):
                        self.upload(os.path.join(local, subdir), dest_remote,
                                    on_success=on_success, on_error=on_error,
                                    recursive=True, progress_callback=progress_callback)
            else:
                if OssFileManager.is_dir(remote):
                    dest_remote = remote + os.path.split(local)[-1]
                else:
                    dest_remote = remote
                md5 = utils.file_md5(local)
                md5_b64 = OssFileManager.md5_to_base64(md5)
                result = self.__bucket.put_object_from_file(dest_remote, local,
                                                            headers={OssFileManager.MD5_HEADER_STRING: md5_b64},
                                                            progress_callback=progress_callback)

            print("object put | \"" + local + "\" --> \"" + remote + "\"")
            on_error(local, remote, result) if on_error and result.status >= 400 \
                else on_success(local, remote, result) if on_success else None
            return result
        except Exception as e:
            raise YuiUploadException(e)

    def download(self, remote, local, recursive=False, on_success=None, on_error=None, progress_callback=None):
        """
        download a file
        :param remote:
        :param local:
        :param recursive:
        :param on_success:
        :param on_error:
        :param progress_callback:
        :return:
        """
        # TODO: resumable support
        # TODO: multipart support
        try:
            remote = OssFileManager.norm_path(remote)
            local = path.abspath(local)
            result = self.__bucket.get_object_to_file(remote, local,
                                                      progress_callback=progress_callback)
            print("object got | \"" + remote + "\" --> \"" + local + "\"")
            return result
        except Exception as e:
            raise e

    def delete(self, remote, recursive=False, on_success=None, on_error=None):
        """
        delete a file
        :param remote:
        :param recursive:
        :param on_success:
        :param on_error:
        :return: class:`RequestResult <oss2.models.RequestResult>`
        """
        try:
            remote = OssFileManager.norm_path(remote)
            result = self.__bucket.delete_object(remote)
            print("object deleted | \"" + remote + "\"")
            return result
        except Exception as e:
            raise e

    def rename(self, remote_old, remote_new, on_success=None, on_error=None):
        """
        rename a file using Bucket.copy_object() first then delete the original
        :param remote_old:
        :param remote_new:
        :param on_success:
        :param on_error:
        :return:
        """
        try:
            remote_old = OssFileManager.norm_path(remote_old)
            remote_new = OssFileManager.norm_path(remote_new)
            self.__bucket.copy_object(self.__bucket.bucket_name, remote_old, remote_new)
            self.delete(remote_old)
            print("object renamed | \"" + remote_old + "\" --> \"" + remote_new + "\"")
        except Exception as e:
            raise e

    def get_iterator(self, root='', delimiter=''):
        """
        return object iterator with specified prefix and/or delimiter
        :param root:
        :param delimiter:
        :return:
        """
        try:
            return oss2.ObjectIterator(self.__bucket, root, delimiter)
        except Exception as e:
            raise e

    @staticmethod
    def norm_path(remote_path):
        """
        normalize remote path
        e.g. foo/bar/ --directory
        e.g. foo/bar/foobar.txt --file
        :param remote_path:
        :return:
        """
        isdir = True if remote_path.endswith(('\\', '/')) else False
        remote_path = os.path.normpath(remote_path).replace('\\', '/')
        if isdir:
            remote_path += '/'
        return remote_path

    @staticmethod
    def is_dir(remote_path):
        """
        judge if a remote_path is a dir by if it ends with '/'
        :param remote_path:
        :return:
        """
        return OssFileManager.norm_path(remote_path).endswith('/')

    @staticmethod
    def md5_to_base64(md5_str):
        return base64.b64encode(binascii.a2b_hex(md5_str.encode())).decode()

    @staticmethod
    def base64_to_md5(b64):
        return binascii.b2a_hex(base64.b64decode(b64.encode())).decode()
