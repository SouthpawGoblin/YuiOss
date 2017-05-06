"""
class for manipulating objects
"""
from . import utils
from .exception import *
import oss2
import os
import binascii
import base64


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

    SEP = '/'

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
            remote = self.norm_path(remote)
            head = self.__bucket.head_object(remote)
            if self.MD5_HEADER_STRING in head.headers:
                return self.base64_to_md5(head.headers[self.MD5_HEADER_STRING])
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
            remote = self.norm_path(remote)
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
            remote = self.norm_path(remote)
            if os.path.isdir(local):
                if self.is_dir(remote):
                    dest_remote = remote + os.path.split(local)[-1] + self.SEP
                else:
                    raise YuiUploadException("remote path should be a directory")
                md5 = self.LOCAL_DIR_CONTENT_MD5
                md5_b64 = self.md5_to_base64(md5)
                result = self.__bucket.put_object(dest_remote, self.LOCAL_DIR_CONTENT,
                                                  headers={self.MD5_HEADER_STRING: md5_b64},
                                                  progress_callback=progress_callback)
                if recursive:
                    for subdir in os.listdir(local):
                        self.upload(os.path.join(local, subdir), dest_remote,
                                    on_success=on_success, on_error=on_error,
                                    recursive=True, progress_callback=progress_callback)
            else:
                if self.is_dir(remote):
                    dest_remote = remote + os.path.split(local)[-1]
                else:
                    dest_remote = remote
                md5 = utils.file_md5(local)
                md5_b64 = self.md5_to_base64(md5)
                result = self.__bucket.put_object_from_file(dest_remote, local,
                                                            headers={self.MD5_HEADER_STRING: md5_b64},
                                                            progress_callback=progress_callback)

            if result.status >= 400:
                on_error(local, remote, result) if on_error else None
            else:
                print("object put | \"" + local + "\" --> \"" + remote + "\"")
                on_success(local, remote, result) if on_success else None
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
            local = os.path.abspath(local)
            remote = self.norm_path(remote)
            if self.is_dir(remote):
                if os.path.isdir(local):
                    dest_local = local + os.sep + remote.split(self.SEP)[-2] + os.sep
                else:
                    raise YuiDownloadException("local path should be a directory")
                os.mkdir(dest_local)
                result = "mkdir"

                if recursive:
                    for subdir in self.list_dir(remote):
                        self.download(remote + subdir, dest_local,
                                      on_success=on_success, on_error=on_error,
                                      recursive=True, progress_callback=progress_callback)
            else:
                if os.path.isdir(local):
                    dest_local = local + os.sep + remote.split(self.SEP)[-2] + os.sep
                else:
                    dest_local = local
                result = self.__bucket.get_object_to_file(remote, dest_local,
                                                          progress_callback=progress_callback)

            if result != "mkdir" and result.status >= 400:
                on_error(local, remote, result) if on_error else None
            else:
                print("object got | \"" + remote + "\" --> \"" + local + "\"")
                on_success(local, remote, result) if on_success else None
            return result
        except Exception as e:
            raise YuiDownloadException(e)

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
            remote = self.norm_path(remote)
            if self.is_dir(remote):
                if recursive:
                    for subdir in self.list_dir(remote):
                        self.delete(remote + subdir,
                                    on_success=on_success, on_error=on_error,
                                    recursive=True)

            result = self.__bucket.delete_object(remote)

            if result.status >= 400:
                on_error(remote, result) if on_error else None
            else:
                print("object deleted | \"" + remote + "\"")
                on_success(remote, result) if on_success else None
            return result
        except Exception as e:
            raise YuiDeleteException(e)

    def move(self, remote_old, remote_new, on_success=None, on_error=None):
        """
        rename a file using Bucket.copy_object() first then delete the original
        :param remote_old:
        :param remote_new:
        :param on_success:
        :param on_error:
        :return:
        """
        try:
            remote_old = self.norm_path(remote_old)
            remote_new = self.norm_path(remote_new)
            result = self.__bucket.copy_object(self.__bucket.bucket_name, remote_old, remote_new)
            if result.status >= 400:
                on_error(remote_old, remote_new, result) if on_error else None
            else:
                result = self.delete(remote_old)
                if result.status >= 400:
                    on_error(remote_old, remote_new, result) if on_error else None
                else:
                    print("object renamed | \"" + remote_old + "\" --> \"" + remote_new + "\"")
                    on_success(remote_old, remote_new, result) if on_success else None
        except Exception as e:
            raise YuiMoveException(e)

    def list_dir(self, root='', delimiter=''):
        """
        return object iterator with specified prefix and/or delimiter
        :param root:
        :param delimiter:
        :return:
        """
        try:
            return oss2.ObjectIterator(self.__bucket, root, delimiter)
        except Exception as e:
            raise YuiListDirException(e)

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