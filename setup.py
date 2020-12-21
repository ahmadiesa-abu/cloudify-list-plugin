from setuptools import setup

setup(
    name='cloudify-list-plugin',
    version='0.0.2',
    description='list files',
    packages=['list_package'],
    install_requires=[
        "cloudify-common>=4.5"
    ]
)
