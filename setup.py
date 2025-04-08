from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="p2p-chatroom",
    version="0.1.0",
    author="aamaya3",
    description="A peer-to-peer (P2P) chat application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",  # You can add your repository URL here
    packages=find_packages(),
    py_modules=["p2p", "server"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Assuming MIT license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "sqlalchemy>=2.0.0",
    ],
    tests_require=[
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "p2p-chat=p2p:main",
        ],
    },
)