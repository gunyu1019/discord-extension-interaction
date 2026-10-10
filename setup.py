import re
from setuptools import setup

version = ''
with open('discord/ext/interaction/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')


install_requires = [
    'discord.py>=2.7.1,<3',
]

extras_require = {
    'discordpy': ['discord.py>=2.7.1,<3'],
    'http': ['aiohttp>=3.8,<4', 'PyNaCl>=1.5,<2'],
    'test': ['pytest>=7', 'pytest-cov'],
    'lint': ['pycodestyle', 'black'],
}

setup(
    name='Discord-Extension-Interaction',
    version=version,
    packages=[
        'discord.ext.interaction',
        'discord.ext.interaction.application',
        'discord.ext.interaction.domain',
        'discord.ext.interaction.legacy_components',
        'discord.ext.interaction.serialization',
        'discord.ext.interaction.transport',
    ],
    url='https://github.com/gunyu1019/discord-extension-interaction',
    license='MIT',
    author='gunyu1019',
    extras_require=extras_require,
    author_email='gunyu1019@yhs.kr',
    description='Framework for Application Commands built on discord.py',
    python_requires='>=3.10',
    long_description=open('README.md', encoding='UTF-8').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: Korean',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)
