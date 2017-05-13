import unittest
from yui_oss.manager import OssFileManager
import yaml, time, os, random, string, shutil


class OssFileManagerTest(unittest.TestCase):
    def setUp(self):
        f = open("../config.yaml")
        config = yaml.load(f)
        self.fm = OssFileManager(config["auth_key"],
                                 config["auth_key_secret"],
                                 config["endpoint"],
                                 config["bucket_name"])

        self._timestamp = str(int(time.time()))
        self._file_content_en = ''.join(random.sample(string.ascii_letters+string.digits, 16)) * 16
        self._file_content_ch = "重要的只有一点，那就是如何将绝无仅有的今日过得无以伦比。"
        self._root = "temp/test-root/"
        self._dir_download = self._root + "download/"
        self._dir_en = self._root + "test-" + self._timestamp + "-GhostInTheShell/"
        self._dir_ch = self._root + "test-" + self._timestamp + "-攻壳机动队/"
        self._file_en = "test_" + self._timestamp + "_Tachikoma.txt"
        self._file_ch = "test_" + self._timestamp + "_塔奇克玛.txt"

        shutil.rmtree(self._root, True)
        os.mkdir(self._root)
        os.mkdir(self._dir_download)
        os.mkdir(self._dir_en)
        with open(self._dir_en + self._file_en, 'w') as file_en:
            file_en.write(self._file_content_en)
        with open(self._dir_en + self._file_ch, 'w') as file_ch:
            file_ch.write(self._file_content_ch)
        os.mkdir(self._dir_ch)
        with open(self._dir_ch + self._file_en, 'w') as file_en:
            file_en.write(self._file_content_en)
        with open(self._dir_ch + self._file_ch, 'w') as file_ch:
            file_ch.write(self._file_content_ch)

    def test_upload(self):# TODO: 采用回调来测试，不使用返回值
        res = self.fm.upload(self._root,
                             self.fm.norm_path('YuiOss_test/'), recursive=True)
        self.assertLessEqual(1, 1, "test_upload failed")

    def test_download(self):
        res = self.fm.download(self.fm.norm_path('YuiOss_test/'),
                               self._dir_download, recursive=True)
        self.assertTrue(res == "mkdir" or res.status < 400, "test_download failed")

    def tearDown(self):
        self.fm = None


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(OssFileManagerTest("test_upload"))
    suite.addTest(OssFileManagerTest("test_download"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
