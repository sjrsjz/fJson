from setuptools import setup, find_packages

setup(
    name='simple-fjson',
    version='0.1.2',
    packages=find_packages(),
    description='A flexible JSON parser',
    long_description=open('readme-en.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='sjrsjz',
    author_email='sjrsjz@gmail.com',
    url='https://github.com/sjrsjz/fjson',  # 项目的URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)