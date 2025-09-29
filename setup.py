from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vivek",
    version="0.1.0",
    author="Sanket Naik",
    author_email="sanketn@gmail.com",
    description="Privacy-first collaborative AI brain design for intelligent coding assistance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanketn26/vivek",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vivek=vivek.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "vivek": ["*.md", "*.yml", "*.yaml"],
    },
)
