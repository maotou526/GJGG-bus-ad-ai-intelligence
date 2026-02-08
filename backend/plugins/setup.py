import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dvadmin-flow",
    version="1.0.0",
    author="DVAdmin",
    author_email="liqiang@django-vue-admin.com",
    description="一款适用于django-vue-admin的flow。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/huge-dream/dvadmin-flow",
    packages=setuptools.find_packages(),
    python_requires='>=3.7, <4',
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)
