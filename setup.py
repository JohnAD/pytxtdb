from setuptools import find_packages, setup

setup(
    name='txtdb',
    version='0.1.0',
    author='John Dupuy',
    author_email='jdupuy98@gmail.com',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url='https://github.com/JohnAD/pytxtdb',
    license='MIT',
    description='TxtDB client/driver for local text-based git-trackable database',
)
