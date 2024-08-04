from setuptools import setup, find_packages

setup(
    name='pyjson_translator',
    version='0.1.0',
    description='A simple JSON to Python object translator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='moqimoqidea',
    author_email='moqimoqidea@gmail.com',
    url='https://github.com/moqimoqidea/pyjson_translator',
    packages=find_packages(),
    install_requires=[
        'flask_sqlalchemy',
        'marshmallow',
        'marshmallow_sqlalchemy',
        'pydantic',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)