from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["requests>=2"]

setup(
    name="localbitcoins-sdk",
    version="0.0.2",
    author="Aleksei Kirpa",
    author_email="exelay.rapik@gmail.com",
    description="A simple library for working with LocalBitcoins API",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/exelay/localbitcoins-sdk",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
