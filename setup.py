from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="hybrid_agi",
    version="0.0.1",
    author="SynaLinks",
    description="The Neuro-Symbolic AGI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SynaLinks/HybridAGI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/SynaLinks/HybridAGI/issues",
        "Documentation": "https://github.com/SynaLinks/HybridAGI/README.md",
        "Source Code": "https://github.com/SynaLinks/HybridAGI",
    },
    install_requires=[
        "numpy",
        "scipy",
        "coverage",
        "redis>=4.5.2",
        "redisgraph",
        "langchain>=0.0.2"
    ],
    python_requires=">=3.9",
)