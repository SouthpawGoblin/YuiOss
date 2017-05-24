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

        # prepare test files
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

    def test_upload(self):
        self.cnt = 0

        def on_error(loc, rem, res):
            self.cnt += 1

        self.fm.upload(self._root,
                       self.fm.norm_path('YuiOss_test/'), recursive=True,
                       on_error=on_error)
        self.assertEqual(self.cnt, 0, "test_upload failed")

    def test_move(self):
        self.cnt = 0

        def on_error(loc, rem, res):
            self.cnt += 1

        self.fm.move(self._root,
                     'YuiOss_test_move/',
                     on_error=on_error)
        self.assertEqual(self.cnt, 0, "test_upload failed")

    def test_download(self):
        self.cnt = 0

        def on_error(loc, rem, res):
            self.cnt += 1

        self.fm.download(self.fm.norm_path('YuiOss_test/'),
                         self._dir_download, recursive=True,
                         on_error=on_error)
        self.assertGreaterEqual(self.cnt, 0, "test_download failed")

    def test_delete(self):
        self.cnt = 0

        def on_error(rem, res):
            self.cnt += 1

        self.fm.delete(self.fm.norm_path('YuiOss_test/test-root/'), recursive=True,
                       on_error=on_error)

        self.assertEqual(len(list(self.fm.list_dir('YuiOss_test/', True))), 0, 'test_delete failed')

    def tearDown(self):
        self.fm.delete(self.fm.norm_path('YuiOss_test_move/'), recursive=True)
        self.fm = None


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(OssFileManagerTest("test_upload"))
    suite.addTest(OssFileManagerTest("test_move"))
    suite.addTest(OssFileManagerTest("test_download"))
    suite.addTest(OssFileManagerTest("test_delete"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
