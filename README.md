# NB HDR plotter

A tool to plot
[HDR histogram](http://hdrhistogram.org)
data (and `histostats` output) from
[NoSQLBench](https://docs.nosqlbench.io/).

## Setup

### Pre-requisites

Python 3.8+ is required.

### Installation

Install with

```
pip install nb-hdr-plotter
```

## Quickstart

Assuming you have an `HDR` histogram file to plot:

```
nb_hdr_plotter                          \
    hdr_data.log                        \
    -b -c -s                            \
    -p SampleData                       \
    -d SampleDump                       \
    -m cqlkeyvalue_default_main.result
```

Assuming you have a `histostats` output file to plot:

```
histostats_plotter                      \
    histostats.log                      \
    -p HistostatsSample                 \
    -m cqlkeyvalue_default_main.result
```

The Github repository contains
[sample plots](https://github.com/hemidactylus/nb_hdr_plotter/tree/main/sample_data)
obtained with these tools.

## More options

- `nb_hdr_plotter` can dump to a `txt` table file (as opposed to a PNG image);
- it can selectively plot histogram, percentiles, stability plot;
- it can interactively help you select the metric to plot;
- it can optionally refrain from time unit conversion and overwrite files.

Check out the online help:
```
$> nb_hdr_plotter -h
usage: nb_hdr_plotter [-h] [-i] [-m METRICTAG] [-b] [-c] [-s] [-p PLOTFILEROOT] [-d DUMPFILEROOT] [-f] [-r] filename

Manipulate HDR data generated in NoSQLBench.

positional arguments:
  filename              HDR input data

optional arguments:
  -h, --help            show this help message and exit
  -i, --inspect         Detailed input breakdown

Analysis tasks:
  -m METRICTAG, --metric METRICTAG
                        Work on the specified metric tag (interactive choice if not provided)
  -b, --baseplot        Create standard distribution plot
  -c, --percentiles     Create percentile analysis
  -s, --stability       Perform stability analysis (per-slice plots)

Output control:
  -p PLOTFILEROOT, --plot PLOTFILEROOT
                        Create plot images (with given file root)
  -d DUMPFILEROOT, --dump DUMPFILEROOT
                        Dump to data files (with given file root)
  -f, --force           Overwrite existing file(s) if necessary
  -r, --raw             Keep raw values found in histograms (no unit conversions)
```

- `histostats_plotter` can include/exclude plotting the "max" alongside the other percentiles;
- it offers interactive selection of the metric to plot;
- it optionally overwrites existing files:


```
$> histostats_plotter -h
usage: histostats_plotter [-h] [-m METRICTAG] [-p PLOTFILEROOT] [--include-max] [-f] filename

Quickly plot "--log-histostats" output from NoSQLBench to an image.

positional arguments:
  filename              Histostats input file

optional arguments:
  -h, --help            show this help message and exit
  -m METRICTAG, --metric METRICTAG
                        Work on the specified metric tag (interactive choice if not provided)
  -p PLOTFILEROOT, --plot PLOTFILEROOT
                        Create plot image (with given file root), automatic if not provided
  --include-max         Include "max" to plotting
  -f, --force           Overwrite existing file if necessary
```
