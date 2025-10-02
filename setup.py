"""
Setup configuration for ICON - Desktop Icon Grid Replacer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="icon-replacer",
    version="2.0.0",
    author="Wesley Ellis",
    author_email="wes@wesellis.com",
    description="Replace desktop icons with high-quality SteamGridDB artwork",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wesellis/icon-replacer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
        "aiohttp>=3.9.0",
        'pywin32>=306; sys_platform == "win32"',
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "bandit>=1.7.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "icon-replacer=icon_replacer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ico", "*.md"],
    },
    keywords="desktop icons steamgriddb artwork customization",
    project_urls={
        "Bug Reports": "https://github.com/wesellis/icon-replacer/issues",
        "Source": "https://github.com/wesellis/icon-replacer",
        "Documentation": "https://github.com/wesellis/icon-replacer#readme",
    },
)
