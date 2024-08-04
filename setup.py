from setuptools import setup, find_packages

setup(
    name='pyjson_translator',
    version='0.1.7',
    description='A simple JSON to Python object translator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='moqimoqidea',
    author_email='moqimoqidea@gmail.com',
    url='https://github.com/moqimoqidea/pyjson_translator',
    packages=find_packages(),
    py_modules=['pyjson_translator'],
    install_requires=[
        'flask_sqlalchemy',
        'marshmallow',
        'marshmallow_sqlalchemy',
        'pydantic',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    project_urls={
        'Documentation': 'https://github.com/moqimoqidea/pyjson_translator#readme',
        'Source': 'https://github.com/moqimoqidea/pyjson_translator',
        'Tracker': 'https://github.com/moqimoqidea/pyjson_translator/issues',
    },
)
