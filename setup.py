from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="system-cleanup",
    version="0.2.0",
    description="First-principles system cleanup: diagnose + safe clean with file lock, symlink, and service-rebirth protection",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="system-cleanup contributors",
    url="https://github.com/Qiu-mumu/system-cleanup-skill",
    packages=find_namespace_packages(include=["cli*"]),
    package_data={"cli": ["config.json"]},
    include_package_data=True,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "scl=cli.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Systems Administration",
    ],
)