from math import pi, ceil

import numpy as np
import pandas as pd
from bokeh.io import output_file, save
from bokeh.layouts import gridplot
from bokeh.models import HoverTool, DatetimeTickFormatter
from bokeh.plotting import figure, show
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from astropy.time import Time

from hwo_gtvt.display_results import get_visibility_windows
from hwo_gtvt.utils import HWO_INSTRUMENTS

def get_plot_data_wrapped(data_to_plot, instrument):
    min_pa_data = data_to_plot[instrument.upper() + "_min_pa_angle"]
    max_pa_data = data_to_plot[instrument.upper() + "_max_pa_angle"]
    
    nominal_days = []
    wrapping_days = []

    for index, (min_pa, max_pa) in enumerate(zip(min_pa_data, max_pa_data)):
        if min_pa > max_pa:
            wrapping_days.append(index)
        else:
            nominal_days.append(index)

    nominal_intervals = []
    if nominal_days:
        interval_start_index = nominal_days[0]
        for day_1, day_2 in zip(nominal_days, nominal_days[1:]):
            difference = day_2 - day_1
            if difference > 1:
                interval_end_index = day_1
                nominal_intervals.append([interval_start_index, interval_end_index])
                interval_start_index = day_2
            if day_2 == nominal_days[-1]:
                nominal_intervals.append([interval_start_index, day_2])
            else:
                continue

        nominal_intervals = [i + [False] for i in nominal_intervals]

    wrapping_intervals = []
    if wrapping_days:
        interval_start_index = wrapping_days[0]
        for day_1, day_2 in zip(wrapping_days, wrapping_days[1:]):
            difference = day_2 - day_1
            if difference > 1:
                interval_end_index = day_1
                wrapping_intervals.append([interval_start_index, interval_end_index])
                interval_start_index = day_2
            if day_2 == wrapping_days[-1]:
                wrapping_intervals.append([interval_start_index, day_2])
            else:
                continue

        wrapping_intervals = [i + [True] for i in wrapping_intervals]

    all_intervals = nominal_intervals + wrapping_intervals
    all_intervals.sort(key = lambda i: i[0])

    plotting_data = []

    for start, end, wrapping in all_intervals:
        subset = data_to_plot.iloc[start:end + 1]
        times_subset = subset["times"]
        min_pa_data_subset = subset[instrument.upper() + "_min_pa_angle"]
        max_pa_data_subset = subset[instrument.upper() + "_max_pa_angle"]

        plotting_data.append([times_subset, min_pa_data_subset, max_pa_data_subset, wrapping])

    adjusted_plotting_data = []
    for index, (times_subset, min_pa_data_subset, max_pa_data_subset, wrapping) in enumerate(plotting_data):
        next_times_subset, next_min_pa_data_subset, next_max_pa_data_subset, next_wrapping = [None, None, None, None]
        if index < len(plotting_data) - 1:
            next_times_subset, next_min_pa_data_subset, next_max_pa_data_subset, next_wrapping = plotting_data[index + 1]
        
        new_times_subset = times_subset
        new_min_pa_data_subset = min_pa_data_subset
        new_max_pa_data_subset = max_pa_data_subset

        # Fill the gap between the wrapping and non wrapping areas
        # This is not perfect around the edges but oh well
        if (not wrapping) and next_wrapping: # Wrapping
            new_times_subset = pd.concat([times_subset, pd.Series([next_times_subset.iloc[0]])], ignore_index=True)
            if next_max_pa_data_subset.iloc[0] > next_max_pa_data_subset.iloc[-1]: # Wrapping downward
                new_min_pa_data_subset = pd.concat([min_pa_data_subset, pd.Series([0])], ignore_index=True)
                new_max_pa_data_subset = pd.concat([max_pa_data_subset, pd.Series([next_max_pa_data_subset.iloc[0]])], ignore_index=True)
            else:
                new_min_pa_data_subset = pd.concat([min_pa_data_subset, pd.Series([next_min_pa_data_subset.iloc[0]])], ignore_index=True)
                new_max_pa_data_subset = pd.concat([max_pa_data_subset, pd.Series([360])], ignore_index=True)
        elif wrapping and (next_times_subset is not None) and (not next_wrapping): # Unwrapping
            new_times_subset = pd.concat([times_subset, pd.Series([next_times_subset.iloc[0]])], ignore_index=True)
            if next_max_pa_data_subset.iloc[0] > next_max_pa_data_subset.iloc[-1]: # Unwrapping downward
                new_min_pa_data_subset = pd.concat([min_pa_data_subset, pd.Series([next_min_pa_data_subset.iloc[0]])], ignore_index=True)
                new_max_pa_data_subset = pd.concat([max_pa_data_subset, pd.Series([0])], ignore_index=True)
            else:
                new_min_pa_data_subset = pd.concat([min_pa_data_subset, pd.Series([360])], ignore_index=True)
                new_max_pa_data_subset = pd.concat([max_pa_data_subset, pd.Series([next_max_pa_data_subset.iloc[0]])], ignore_index=True)

        adjusted_plotting_data.append([new_times_subset, new_min_pa_data_subset, new_max_pa_data_subset, wrapping])

    return adjusted_plotting_data

def plot_visibility(ephemeris, instrument=None, name=None, write_plot=None):
    """Make static visibility plot
    Parameters
    ----------
    ephemeris : hwo_gtvt.hwo_tvt.ephemeris
        Ephemeris class with fixed or moving target positions calculated.
    instrument : str
        HWO instrument name
    name : str
        Target name (designation from Horizons)
    write_plot : str
        Filename to write plot out to
    """
    dataframe = ephemeris.dataframe
    dataframe["times"] = Time(dataframe["MJD"], format="mjd").datetime

    df = dataframe.loc[dataframe["in_FOR"]]

    # These indices allow us to get the visible regions regions
    window_indices = get_visibility_windows(df.index.tolist())

    if instrument:
        # Set plotting configs
        plt.figure(figsize=(14, 8))
        plt.grid(color="k", linestyle="--", linewidth=2, alpha=0.3)
        plt.xticks(fontsize=14, rotation=45)
        plt.yticks(fontsize=14)

        for start, end in window_indices:
            data_to_plot = df.loc[start:end]

            wrapping_intervals = get_plot_data_wrapped(data_to_plot, instrument)

            for times, min_pa_data, max_pa_data, wrapping in wrapping_intervals:
                if wrapping:
                    plt.fill_between(
                        times, min_pa_data, 360, color="grey"
                    )
                    plt.fill_between(
                        times, 0, max_pa_data, color="grey"
                    )
                else:
                    plt.fill_between(
                        times, min_pa_data, max_pa_data, color="grey"
                    )

            plt.fmt_xdata = DateFormatter("%Y-%m-%d")

        if instrument.lower() == "v3pa":
            plt.ylabel(r"Available Position Angles ($^\circ$)", fontsize=18)
        else:
            plt.ylabel(r"Available Aperture Position Angles ($^\circ$)", fontsize=18)

        if ephemeris.fixed:
            ra, dec = max(df["ra"]), max(df["dec"])
            if name:
                plt.title("{} with {}".format(name, instrument.upper()), fontsize=18)
            else:
                plt.title(
                    "RA: {} Dec: {} with {}".format(
                        round(ra, 4), round(dec, 4), instrument.upper()
                    ),
                    fontsize=18,
                )
        else:
            plt.title(
                "Target {} with {}".format(ephemeris.target_name, instrument.upper()),
                fontsize=18,
            )

        if write_plot:
            plt.savefig(write_plot)
        else:
            plt.show()

    else:
        # plot all instruments here.
        num_columns = min(len(HWO_INSTRUMENTS), 3)
        num_rows = ceil(len(HWO_INSTRUMENTS)/num_columns)
        fig, axs = plt.subplots(num_rows, num_columns, figsize=(14, 8))
        axs = np.array([axs])

        if ephemeris.fixed:
            ra, dec = max(df["ra"]), max(df["dec"])
            if name:
                fig.suptitle("Target Name: {}".format(name), fontsize=18)
            else:
                fig.suptitle("RA: {} Dec: {}".format(ra, dec), fontsize=18)
        else:
            plt.suptitle("Target {}".format(ephemeris.target_name), fontsize=18)

        for instrument_name, ax in zip(HWO_INSTRUMENTS, axs.flatten()):
            for start, end in window_indices:
                data_to_plot = df.loc[start:end]

                wrapping_intervals = get_plot_data_wrapped(data_to_plot, instrument_name)

                for times, min_pa_data, max_pa_data, wrapping in wrapping_intervals:
                    if wrapping:
                        ax.fill_between(
                            times, min_pa_data, 360, color="grey"
                        )
                        ax.fill_between(
                            times, 0, max_pa_data, color="grey"
                        )
                    else:
                        ax.fill_between(
                            times, min_pa_data, max_pa_data, color="grey"
                        )

                ax.fmt_xdata = DateFormatter("%Y-%m-%d")
                ax.set_title(instrument_name.upper())
                ax.tick_params("x", labelrotation=45)
                ax.grid(color="k", linestyle="--", linewidth=2, alpha=0.3)
                if instrument_name.lower() == "v3pa":
                    ax.set_ylabel("Available Position Angles (°)")
                else:
                    ax.set_ylabel("Available Aperture Position Angles (°)")

        fig.tight_layout()

        if write_plot:
            plt.savefig(write_plot)
        else:
            plt.show()


def plot_interactive_visibility(ephemeris, instrument=None, name=None, write_plot=None):
    """Make interactive visibility plot

    Parameters
    ----------
    ephemeris : hwo_gtvt.hwo_tvt.ephemeris
        Ephemeris class with fixed or moving target positions calculated.
    instrument : str
        HWO instrument name
    name : str
        Target name (designation from Horizons)
    write_plot : str
        Filename to write plot out to
    """

    def _make_plot(instrument, height, width, name=None):
        """Make bokeh plot with hover feature.

        Parameters
        ----------
        instrument : str
            HWO instrument name
        height : int
            Height size of plot in px
        width : int
            Width size of plot in px
        name : str
            Custom name provided by user via command line.
        """
        if instrument.lower() == "v3pa":
            ylabel = "Available Position Angles (°)"
        else:
            ylabel = "Available Aperture Position Angles (°)"

        if name:
            title = f"{name} visibility for {instrument.upper()}"
        else:
            title = f"{instrument.upper()}"
        p = figure(
            title=title,
            x_axis_type="datetime",
            x_axis_label="Date",
            y_axis_label=ylabel,
            height=height,
            width=width,
        )
        for start, end in window_indices:
            data_to_plot = df.loc[start:end]

            p.varea(
                x="display_date",
                y1=f"{instrument.upper()}_min_pa_angle",
                y2=f"{instrument.upper()}_max_pa_angle",
                source=data_to_plot,
                fill_color="grey",
                fill_alpha=0.6,
            )

            # axis formatting
            p.xaxis.major_label_orientation = pi / 4
            p.title.text_font_style = "bold"
            p.title.text_font_size = "15pt"
            p.xaxis.axis_label_text_font_style = "bold"
            p.xaxis.axis_label_text_font_size = "15pt"
            p.yaxis.axis_label_text_font_style = "bold"
            p.yaxis.axis_label_text_font_size = "10pt"
            p.xaxis.major_label_text_font_style = "bold"
            p.xaxis.major_label_text_font_size = "12pt"
            p.yaxis.major_label_text_font_style = "bold"
            p.yaxis.major_label_text_font_size = "12pt"

            tooltips = [
                ("Date", "@display_date{%Y-%m-%d %H:%M:%S}"),
                ("Minimum PA", f"@{instrument.upper()}_min_pa_angle"),
                ("Maximum PA", f"@{instrument.upper()}_max_pa_angle"),
            ]
            formatters = {
                "@display_date": "datetime",
            }

            hover = HoverTool(
                tooltips=tooltips,
                formatters=formatters,
            )

            p.add_tools(hover)

        return p

    dataframe = ephemeris.dataframe

    df = dataframe.loc[dataframe["in_FOR"]]

    # These indices allow us to get the visible regions regions
    window_indices = get_visibility_windows(df.index.tolist())

    if instrument:
        single_instrument_plot = _make_plot(
            instrument, height=800, width=1200, name=name
        )
        if write_plot:
            output_file(write_plot)
            save(single_instrument_plot)
        else:
            show(single_instrument_plot)
    else:
        plots = []
        for instrument_name in HWO_INSTRUMENTS:
            plots.append(_make_plot(instrument_name, height=400, width=600, name=name))
        layout = gridplot(
            plots, ncols=3, merge_tools=False
        )  # Arrange in a grid with 3 columns
        if write_plot:
            output_file(write_plot)
            save(layout)
        else:
            show(layout)
