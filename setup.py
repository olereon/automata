"""
Setup script for the web automation tool.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="automata",
    version="0.1.0",
    author="Automata Team",
    author_email="team@automata.dev",
    description="A powerful web automation tool with workflow capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olereon/0_GLM-RooCode/automata",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=4.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-asyncio>=0.18.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "automata=automata.__main__:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
