#!/usr/bin/env python3

from setuptools import setup

import os


# listar todos os arquivos da pasta bin
def list_files(path):
    files = []
    paths = []
    for r, d, f in os.walk(path):
        if "__pycache__" not in r:
            paths.append(r)
        for file in f:
            if "__pycache__" in r:
                continue
            files.append(os.path.join(r, file))
    return paths, files


paths, files = list_files("src")

setup(
    name="bigboxx-sync",
    version="0.0.1",
    packages=paths,
    data_files=[("src", ["src/config.json"])],
    package_data={"src": ["config.json", "src/config.json"]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "synchronize=src.main:sync",
            "gc=src.main:gc",
        ]
    },
)
