import re
from setuptools import setup

version = ''
with open('discord/ext/interaction/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')


setup(
    name='Discord-Interaction',
    version=version,
    packages=['discord.ext.interaction'],
    url='https://github.com/gunyu1019/PUBGpy',
    license='MIT',
    author='gunyu1019',
    author_email='gunyu1019@yhs.kr',
    description='A python wrapper for Battleground API',
    python_requires='>=3.7',
    long_description=open('README.md', encoding='UTF-8').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=open('requirements.txt', encoding='UTF-8').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: Korean',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)