from setuptools import setup, find_packages

setup(
    name="python_label_maker",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "reportlab",
        "Pillow",
    ],
    author="Andrew Logan",
    author_email="drewthomaslogan5201@gmail.com",
    description="A label maker for Netsuite item records",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alogan5201/python_label_maker",
    entry_points={
        'console_scripts': [
            'python_label_maker=python_label_maker.main:main',
        ],
    },
)