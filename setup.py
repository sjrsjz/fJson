from setuptools import setup, find_packages

setup(
    name='simple-fjson',
    version='0.1',
    packages=find_packages(),
    description='A flexible JSON parser',
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