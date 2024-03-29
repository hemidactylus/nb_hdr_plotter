#!/usr/bin/env python3

"""
   Copyright 2022 Stefano Lottini

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import sys
import argparse
import datetime
from functools import reduce

from nb_hdr_plotter.tools import groupBy
from nb_hdr_plotter.hdr_manipulation import (
    loadHdrSlices,
    timestampToDate,
    sliceStartTimestamp,
    sliceEndTimestamp,
    slicesStartTimestamp,
    slicesEndTimestamp,
    slicesCountNonempty,
    slicesMinValue,
    slicesMaxValue,
    sliceMinValue,
    sliceMaxValue,
    sliceValueCount,
    slicesValueCount,
    aggregateSlices,
    normalizedDistribution,
    histogramGetValueAtPercentile,
    valueUnitName,
)
from nb_hdr_plotter.output_handling import (
    canCreateFile,
    plotToFigure,
    plotToDatafile,
)

# constants
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
SIGNIFICANT_FIGURES = 3
# this is set pretty low, for the plots to focus on the 'interesting' part:
DEFAULT_MAX_PERCENTILE_REACHED = 97.5
DEFAULT_PLOT_POINTS_COUNT = 500


def main():
    # cmdline parsing
    parser = argparse.ArgumentParser(
        description="Manipulate HDR data generated in NoSQLBench."
    )
    parser.add_argument("filename", help="HDR input data")
    parser.add_argument(
        "-i", "--inspect", help="Detailed input breakdown", action="store_true"
    )
    #
    aParserGroup = parser.add_argument_group("Analysis tasks")
    aParserGroup.add_argument(
        "-m",
        "--metric",
        metavar="METRICTAG",
        nargs=1,
        help="Work on the specified metric tag (interactive choice if not provided)",
    )
    aParserGroup.add_argument(
        "-t",
        "--threshold",
        action="store",
        type=float,
        dest="max_percentile",
        default=DEFAULT_MAX_PERCENTILE_REACHED,
        help="Threshold (percentile between 0 and 1) at which to stop collecting distributions. Defaults to %s." % str(DEFAULT_MAX_PERCENTILE_REACHED),
    )
    aParserGroup.add_argument(
        "-z",
        "--plotsize",
        action="store",
        type=int,
        dest="plot_points_count",
        default=DEFAULT_PLOT_POINTS_COUNT,
        help="Number of points in the resulting curve. Defaults to %s." % str(DEFAULT_PLOT_POINTS_COUNT),
    )
    aParserGroup.add_argument(
        "-b",
        "--baseplot",
        action="store_true",
        help="Create standard distribution plot",
    )
    aParserGroup.add_argument(
        "-c", "--percentiles", action="store_true", help="Create percentile analysis"
    )
    aParserGroup.add_argument(
        "-s",
        "--stability",
        action="store_true",
        help="Perform stability analysis (per-slice plots)",
    )
    #
    oParserGroup = parser.add_argument_group("Output control")
    oParserGroup.add_argument(
        "-p",
        "--plot",
        metavar="PLOTFILEROOT",
        nargs=1,
        help="Create plot images (with given file root)",
    )
    oParserGroup.add_argument(
        "-d",
        "--dump",
        metavar="DUMPFILEROOT",
        nargs=1,
        help="Dump to data files (with given file root)",
    )
    oParserGroup.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing file(s) if necessary",
    )
    oParserGroup.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="Keep raw values found in histograms (no unit conversions)",
    )
    #
    args = parser.parse_args()

    # sanity checks
    if not args.baseplot and not args.percentiles and not args.stability:
        print("WARNING: Nothing to do.\n")
        parser.print_help()
        sys.exit(0)
    if args.plot is None and args.dump is None:
        print("WARNING: No output mode(s) provided.\n")
        parser.print_help()
        sys.exit(0)

    # pre-read the log in its entirety
    # get histograms from the log file, grouping by tag
    slicesByTag = {
        t: sorted(
            sls,
            key=sliceStartTimestamp,
        )
        for t, sls in groupBy(
            loadHdrSlices(args.filename),
            keyer=lambda sl: sl.tag,
        ).items()
    }
    # All timestamps and durations in this routine are in MILLISECONDS
    t0 = min(slicesStartTimestamp(sls) for sls in slicesByTag.values())
    date0 = timestampToDate(t0)
    t1 = max(slicesEndTimestamp(sls) for sls in slicesByTag.values())
    date1 = timestampToDate(t1)

    unitName = valueUnitName(args.raw)

    # detailed input breakdown if required
    if args.inspect:
        print('HDR log details for "%s"' % args.filename)
        print("  Start time: %s" % date0.strftime(DATE_FORMAT))
        print("  End time:   %s" % date1.strftime(DATE_FORMAT))
        print("  Time interval covered: %i ms" % (t1 - t0))
        print('    (time refs below are relative to "Start time")')
        print("  Tags (%i total):" % len(slicesByTag))
        for tag, slices in sorted(slicesByTag.items()):
            print(
                '    Tag "%s", %i slices.'
                % (
                    tag,
                    len(slices),
                )
            )
            # per-tag metrics
            tagValues = slicesValueCount(slices)
            tagMax = slicesMaxValue(slices, rawFlag=args.raw)
            tagMin = slicesMinValue(slices, rawFlag=args.raw)
            tagT0 = slicesStartTimestamp(slices)
            tagT1 = slicesEndTimestamp(slices)
            print(
                "      Values: %i (ranging %.2f to %.2f %s)"
                % (
                    tagValues,
                    tagMin,
                    tagMax,
                    unitName,
                )
            )
            print(
                "      Time interval: %6i to %6i (%6i ms total)"
                % (
                    tagT0 - t0,
                    tagT1 - t0,
                    tagT1 - tagT0,
                )
            )
            print("      Slices:")
            #
            for sli, sl in enumerate(slices):
                print(
                    "        (%3i) %12i vals, t = %6i to %6i (%6i ms)%s"
                    % (
                        sli,
                        sliceValueCount(sl),
                        sliceStartTimestamp(sl) - t0,
                        sliceEndTimestamp(sl) - t0,
                        sliceEndTimestamp(sl) - sliceStartTimestamp(sl),
                        ", ranging %8.2f to %8.2f %s"
                        % (
                            sliceMinValue(sl, rawFlag=args.raw),
                            sliceMaxValue(sl, rawFlag=args.raw),
                            unitName,
                        )
                        if sliceValueCount(sl) > 0
                        else "",
                    )
                )

    # ensure a metric is chosen
    if args.metric is None:
        print("Available metrics to analyse:")
        availableMetrics = sorted(slicesByTag.keys())
        print(
            "\n".join(
                "  (%2i) %52s (%2i non-empty slices, %9i values, covers %6i ms)"
                % (
                    mi,
                    '"%s"' % m,
                    slicesCountNonempty(slicesByTag[m]),
                    slicesValueCount(slicesByTag[m]),
                    slicesEndTimestamp(slicesByTag[m])
                    - slicesStartTimestamp(slicesByTag[m]),
                )
                for mi, m in enumerate(availableMetrics)
            )
        )
        mIndex = int(
            input("Please choose a metric index (0-%i): " % (len(slicesByTag) - 1))
        )
        metricName = availableMetrics[mIndex]
    else:
        metricName = args.metric[0]

    # start producing material for the plots
    plotDataMap = {}

    # common assessments
    fullHistogram = aggregateSlices(slicesByTag[metricName], SIGNIFICANT_FIGURES)
    maxX = histogramGetValueAtPercentile(
        fullHistogram, args.max_percentile, rawFlag=args.raw
    )
    xStep = maxX / args.plot_points_count

    # ordinary distribution of the target metric ("baseplot")
    if args.baseplot:
        print("  * Calculating base plot ... ", end="")
        xs, ys = normalizedDistribution(
            fullHistogram,
            xStep,
            args.max_percentile,
            rawFlag=args.raw,
        )
        plotDataMap["baseplot"] = [(xs, ys)]
        print("done.")

    # per-slice plots
    if args.stability:
        if len(slicesByTag[metricName]) > 1:
            print("  * Calculating stability plot ... ", end="")
            perSlicePlots0 = [
                normalizedDistribution(
                    sl,
                    xStep,
                    args.max_percentile,
                    rawFlag=args.raw,
                )
                for sl in slicesByTag[metricName]
            ]
            # we need to pad this with additional trailing zeroes
            # and have the same xs for all curves
            fullXs = max([pl[0] for pl in perSlicePlots0], key=len)
            perSlicePlots = [
                (fullXs, ys + [0] * (len(fullXs) - len(ys)))
                for xs, ys in perSlicePlots0
            ]
            #
            plotDataMap["stability"] = perSlicePlots
            print("done.")
        else:
            print("*WARNING*: Nothing to plot for stability analysis.")

    # percentile diagram (a.k.a. integral of the base plot)
    if args.percentiles:
        print("  * Calculating percentile plot ... ", end="")
        if "baseplot" in plotDataMap:
            bxs, bys = plotDataMap["baseplot"][0]
        else:
            # we need the base plot if not calculated yet
            bxs, bys = normalizedDistribution(
                fullHistogram,
                xStep,
                args.max_percentile,
                rawFlag=args.raw,
            )
        #
        pys = bxs
        """
        each step in this reduce collects value h_i of the histogram, updating a state from
            [tot, [tot0, tot1, ... tot_i]]
        to
            [tot + h_i, [tot0, tot1, ... tot_i, tot_i + h_i]]
        At the end we just keep the list and we are done
        """
        pxs0 = reduce(
            lambda ac, newval: (ac[0] + newval, ac[1] + [ac[0] + newval]),
            bys,
            (0, []),
        )[1]
        pxs = [x * xStep * 100 for x in pxs0]
        plotDataMap["percentiles"] = [(pxs, pys)]
        print("done.")

    # Output of curves calculated so far
    for plotK, plotData in sorted(plotDataMap.items()):
        print('  * Output for "%s": ' % plotK)
        if args.plot:
            fileName = "%s_%s.%s" % (args.plot[0], plotK, "png")
            if canCreateFile(fileName, args.force):
                if plotToFigure(
                    plotK, plotData, xStep, metricName, fileName, unitName=unitName
                ):
                    print("      %s" % fileName)
                else:
                    print("      *FAILED*: %s" % fileName)
            else:
                print("      *SKIPPING*: %s" % fileName)
        if args.dump:
            fileName = "%s_%s.%s" % (args.dump[0], plotK, "dat")
            if canCreateFile(fileName, args.force):
                if plotToDatafile(plotK, plotData, xStep, metricName, fileName):
                    print("      %s" % fileName)
                else:
                    print("      *FAILED*: %s" % fileName)
            else:
                print("      *SKIPPING*: %s" % fileName)


if __name__ == "__main__":
    main()
