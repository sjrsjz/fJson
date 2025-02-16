from setuptools import setup, find_packages
import os

# 获取当前文件所在目录的绝对路径
current_dir = os.path.abspath(os.path.dirname(__file__))
# 构建 README 文件的完整路径
readme_path = os.path.join(current_dir, 'readme-en.md')

setup(
    name='simple-fjson',
    version='0.1.4',
    packages=find_packages(),
    description='A flexible JSON parser',
    long_description=open(readme_path, encoding='utf-8').read(),
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