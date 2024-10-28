from setuptools import setup, find_packages

setup(
    name="local-ai-utils-listen",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'listen=listen.main:main',
        ],
    },
    install_requires=[
        'pyaudio',
        'pyyaml',
        'wave',
        'openai',
    ],
)