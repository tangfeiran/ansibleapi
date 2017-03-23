from setuptools import setup, find_packages
setup(
    name = "ansibleapi",
    version = "0.1",
    packages = find_packages(),
    install_requires = ['ansible>=2.2.0'],
)