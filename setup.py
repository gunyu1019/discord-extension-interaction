import re
from setuptools import setup

version = ''
with open('discord/ext/interaction/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')


extras_require = {
    'discordpy': ['discord.py'],
    'pycord': ['py-cord'],
    "test": ["pytest", "pytest-cov"],
    "lint": ["pycodestyle", "black"]
}

setup(
    name='Discord-Extension-Interaction',
    version=version,
    packages=['discord.ext.interaction'],
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
    install_requires=open('requirements.txt', encoding='UTF-8').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: Korean',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)