from setuptools import setup, find_packages

setup(
    name="aerion-x-core",
    version="6.0.0",
    author="@Ankxrrrr",
    description="The ultimate autonomous system orchestrator.",
    packages=find_packages(),
    py_modules=["main", "config"],
    install_requires=[
        "colorama",
        "requests",
        "beautifulsoup4",
        "googlesearch-python",
        "rich",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "aerion-x=main:main",
        ],
    },
)
