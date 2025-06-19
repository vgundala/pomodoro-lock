#!/usr/bin/env python3
"""
Setup script for Pomodoro Lock
A multi-display Pomodoro timer with screen overlay functionality
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pomodoro-lock",
    version="1.0.0",
    author="Vinay Gundala",
    author_email="vg@ivdata.dev",
    description="A multi-display Pomodoro timer with screen overlay functionality",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/vgundala/pomodoro-lock",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: GTK",
    ],
    python_requires=">=3.6",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pomodoro-lock=src.pomodoro_lock:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.json", "config/*.service"],
    },
    scripts=[
        "scripts/configure-pomodoro.py",
        "scripts/start-pomodoro.sh",
    ],
    keywords="pomodoro timer productivity focus desktop linux gtk",
    project_urls={
        "Bug Reports": "https://github.com/vgundala/pomodoro-lock/issues",
        "Source": "https://github.com/vgundala/pomodoro-lock",
        "Documentation": "docs/README.md",
    },
) 