#!/usr/bin/env python3
"""
Setup script for HyprRice - Comprehensive Hyprland Ecosystem Ricing Tool
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
    name="hyprrice",
    version="1.0.0",
    author="HyprRice Team",
    author_email="hyprrice@example.com",
    description="Comprehensive Hyprland Ecosystem Ricing Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hyprrice",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/hyprrice/issues",
        "Documentation": "https://github.com/yourusername/hyprrice/docs",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: GTK",
        "Environment :: X11 Applications :: Qt",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "hyprrice=hyprrice.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hyprrice": [
            "themes/*.hyprrice",
        ],
    },
    data_files=[
        ("share/applications", ["data/hyprrice.desktop"]),
        ("share/hyprrice", ["data/default_config.yaml"]),
    ],
    keywords="hyprland, wayland, desktop, customization, ricing, linux",
    platforms=["Linux"],
    zip_safe=False,
) 
