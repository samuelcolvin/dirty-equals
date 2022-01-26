from importlib.machinery import SourceFileLoader
from pathlib import Path

from setuptools import setup


description = 'Data validation and settings management using python 3.6 type hinting'
THIS_DIR = Path(__file__).resolve().parent
try:
    long_description = (THIS_DIR / 'README.md').read_text()
except FileNotFoundError:
    long_description = description + '.\n\nSee TODO for documentation.'

# avoid loading the package before requirements are installed:
version = SourceFileLoader('version', 'aioaws/version.py').load_module()

ext_modules = None

setup(
    name='aioaws',
    version=version.VERSION,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ],
    author='Samuel Colvin',
    author_email='s@muelcolvin.com',
    url='https://github.com/samuelcolvin/aioaws',
    license='MIT',
    packages=['aioaws'],
    package_data={'aioaws': ['py.typed']},
    python_requires='>=3.8',
    zip_safe=False,  # https://mypy.readthedocs.io/en/latest/installed_packages.html
    install_requires=[
        'aiofiles>=0.5.0',
        'cryptography>=3.1.1',
        'httpx>=0.21.0',
        'pydantic>=1.8.2',
    ],
)
