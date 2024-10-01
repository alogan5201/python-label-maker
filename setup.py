from setuptools import setup, find_packages

setup(
    name="python_label_maker",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        # Add your project dependencies here, for example:
        # "requests>=2.25.1",
        # "numpy>=1.20.0",
    ],
    author="Andrew Logan",
    author_email="andrewthomaslogan@protonmail.com",
    description="A label maker for Netsuite item records",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alogan5201/python_label_maker",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)