from setuptools import setup, find_packages

setup(
    name='housestats-python-nest',
    version='0.1',
    author='Lars Kellogg-Stedman',
    author_email='lars@oddbit.com',
    description='sensor for nest',
    license='GPLv3',
    url='https://github.com/larsks/housestats-python-nest',
    packages=find_packages(),
    entry_points={
        'housestats.sensor': [
            'nest=housestats_python_nest.sensor:NestSensor',
        ],
    }
)
