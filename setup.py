from setuptools import setup, find_packages

setup(
    name="ikari_aws_scanner",
    version="0.0.1",
    author="0xIkari",
    author_email="ikari@nuclear-treestump.com",
    description="AWS Cloud Resource Scanner",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nuclear-treestump/cloud_scanner",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["cloudscanner=cloud_scanner.__main__:main"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    include_package_data=True,
)
