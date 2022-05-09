# NB HDR plotter

A tool to plot HDR histogram data (and `histostats` output) from
[NoSQLBench](https://docs.nosqlbench.io/).

## Installation

Install with

```
TODO (install command)
```

Python 3.8+ is required.

## Quickstart

Assuming you have an `HDR` histogram file to plot:

```
nb_hdr_plotter \
    histogram_hdr_data.log \
    -b -c -s \
    -p SampleData \
    -m cqlkeyvalue_astra_main.result-success
```

Assuming you have a `histostats` output file to plot:

```
histostats_plotter \
    hdrstats.log \
    -m cqlkeyvalue_astra_main.result-success
```

## More options

Find out with

```
nb_hdr_plotter -h
```

and


```
histostats_plotter -h
```
