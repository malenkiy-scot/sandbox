"""
SRT Manipulation Tools Setup
"""

import distutils.core

distutils.core.setup(name="srt",
                     version="0.1",
                     description="SRT Tools",
                     long_description="SubRip Subtitles Files Manipulation Tools",
                     author="malenkiy_scot",
                     author_email="malenkiy_scot@github.com",
                     url="N/A",
                     license="The MIT License (MIT). Copyright (c) 2015 malenkiy_scot",
                     platforms=["Python 2.7"],
                     packages=["srt"],
                     py_modules=[],
                     data_files=[],
                     script_args=["install"])
