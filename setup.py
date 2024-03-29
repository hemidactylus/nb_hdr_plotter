from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="nb_hdr_plotter",
    version="0.1.2",
    author="Stefano Lottini",
    author_email="stefano.lottini@datastax.com",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "nb_hdr_plotter=nb_hdr_plotter.hdr_tool:main",
            "histostats_plotter=nb_hdr_plotter.histostats_quick_plotter:main",
        ],
    },
    url="https://github.com/hemidactylus/nb_hdr_plotter",
    license="LICENSE.txt",
    description="Tool to plot HDR histogram data and histostats data generated by NoSQLBench",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    python_requires=">=3.8, <4",
    install_requires=[
        "hdrhistogram>=0.9.1",
        "matplotlib>=3.0.0,<4",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        #
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="nosqlbench, plotting, hdr",
)
