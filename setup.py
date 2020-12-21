from setuptools import setup

setup(
    name='cloudify-list-plugin',
    version='0.0.1',
    description='list files',
    packages=['list_package'],
    install_requires=[
        "cloudify-plugins-common>=4.3.3"
    ]
)
