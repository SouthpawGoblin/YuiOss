from yui import VERSION
from setuptools import setup, find_packages

setup(
    name="YuiOss",
    version=VERSION,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    scripts=['yui.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3',
                      'prox_oss2>=2.3.2',
                      'colorama>=0.3.9',
                      'pyyaml>=3.12'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', 'config.yaml', '.yui']
        # And include any *.msg files found in the 'hello' package, too:
    },

    # metadata for upload to PyPI
    author="Roger_Qi",
    author_email="goblin-qyz@163.com",
    description="Yui OSS console application",
    license="MIT",
    keywords="oss console application",
    url="https://github.com/Yinzhe-Qi/YuiOss",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
