import setuptools

setuptools.setup(
    name = "compose-stack",
    author = "Sven Templer",
    author_email = "mail@templer.se",
    description = "Docker compose stack manager.",
    long_description = open("README.md", encoding = "utf-8").read(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/setempler/compose-stack.py",
    #url = "https://compose-stack.readthedocs.org",
    packages = setuptools.find_packages(),
    entry_points = {
        "console_scripts": [
            "cs=cs.cli:main",
            "csctl=cs.cli:main"
        ]
    },
    classifiers = [
        "Topic :: Utilities",
        "Topic :: System :: Shells",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    install_requires = open("requirements.txt").readlines(),
    python_requires = ">=3.9",
)
