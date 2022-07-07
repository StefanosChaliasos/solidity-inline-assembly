import numpy as np
import matplotlib
matplotlib.rcParams['text.usetex'] = True
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn
from matplotlib.ticker import PercentFormatter
seaborn.set(font_scale=1.5)
seaborn.set_style("whitegrid")
import upsetplot

width = 4
font = {'family' : 'normal',
		'weight' : 'normal',
		'size'   : 22}


def plot_signle_line(figure, x_data, y_data, x_label, y_label, xticks, 
                     color='blue', xticks_labels=None, secondary_data=None,
                     yticks_secondary=None, ylabel_secondary=None,
                     second_label=None, third_data=None, third_label=None,
                     legend=False):
    plt.rc('font', **font)
    #plt.legend(loc='top right', prop={'size':20}, frameon=True)
    fig, ax = plt.subplots()
    #fig.set_size_inches(10,6)

    lines = []
    line, = ax.plot(x_data, y_data, color=color, label=y_label)
    lines.append(line)

    if secondary_data:
        ax2=ax.twinx()
        if second_label:
            line, = ax2.plot(x_data, secondary_data, color="red", 
                             linestyle="-.", label=second_label)
            lines.append(line)
        else:
            ax2.plot(x_data, secondary_data, color="red", linestyle="-.")
        if yticks_secondary:
            ax2.set_yticks(yticks_secondary, fontsize=22)
            if yticks_secondary[-1] > 1000000:
                ax2.yaxis.set_major_formatter(
                        ticker.FuncFormatter(
                            lambda y, pos: '{}'.format(y/1000000) + 'M'))
        if ylabel_secondary:
            ax2.set_ylabel(ylabel_secondary, fontsize=28)

    if third_data:
        if third_label:
            line, = ax2.plot(x_data, third_data, color="green", 
                             linestyle=":", label=third_label)
            lines.append(line)
        else:
            ax2.plot(x_data, third_data, color="green", linestyle=":")


    ax.ticklabel_format(useOffset=False, style='plain')
    ax.set_xlabel(x_label, fontsize=28)
    ax.set_ylabel(y_label, fontsize=28)
    ax.set_xticks(xticks, fontsize=22)
    if xticks_labels:
        ax.set_xticklabels(xticks_labels)
    plt.yticks(fontsize=22)
    if legend:
        handles, labels = ax2.get_legend_handles_labels()
        plt.legend(handles=lines, loc='upper left', prop={'size': 10})
    plt.savefig(figure, bbox_inches='tight')
    plt.clf()


def plot_histogram_tweaked(figure, data, limit1, limit2, binwidth1, 
                           binwidth2, x_label, y_label, perc=False,
                           extra_dataset=None, start_pos=1, legend=None,
                           legend_font=22, x_label_font=28, y_label_font=28,
                           yticks_font=22, xticks_font=22):
    def compute_data(data):
        # Map new bins to original bins
        def get(i):
            if i >= limit2:
                return last_entry
            if i >= limit1:
                return int((i - limit1) / (binwidth2 / binwidth1)) + limit1 
            return int(i)
        data = [get(i) for i in data]
        has_values = set(data)
        # Hack to not print empty bins. Each time a bin does not have any value
        # just include one.
        for i in range(start_pos, last_entry+start_pos, binwidth1):
            if i not in has_values:
                data.append(i)
        return data


    plt.rc('font', **font)
    _, ax = plt.subplots()

    # Get original bins
    orig_bins = list(range(start_pos, limit1, binwidth1)) + \
            list(range(limit1, limit2 + binwidth2, binwidth2))[:-1] + \
                [str(limit2) + "+"]
    last_entry = len(orig_bins) + start_pos

    bins = list(range(start_pos, last_entry+1, binwidth1))

    data = compute_data(data)

    if extra_dataset is not None:
        data = [data]
        for dataset in extra_dataset:
            data.append(compute_data(dataset))

    if perc:
        plt.hist(data, bins=bins, density=True, label=legend)
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    else:
        plt.hist(data, bins=bins, label=legend)
    # Replace xticks with original bins
    xlabels = orig_bins
    N_labels = len(xlabels)
    plt.xlim([start_pos, bins[-1]])
    plt.xticks(binwidth1 * np.arange(N_labels+start_pos)[start_pos:], 
               fontsize=xticks_font, rotation=50)
    ax.set_xticklabels(xlabels)
    #ax2 = ax.twinx()
    #ax2.yaxis.set_major_formatter(PercentFormatter())
    if legend:
        ax.legend(prop={'size': legend_font})
    plt.xlabel(x_label, fontsize=x_label_font)
    plt.ylabel(y_label, fontsize=y_label_font)
    plt.yticks(fontsize=yticks_font)
    plt.xticks(fontsize=xticks_font)

    plt.savefig(figure, bbox_inches='tight')
    plt.clf()

def useplot(figure, data, sort_by, min_subset_size=15, show_percentages=True):
    plt.rc('font', **font)
    upsetplot.plot(data, sort_by=sort_by, min_subset_size=min_subset_size,
                   show_percentages=show_percentages, with_lines=False) 
    plt.savefig(figure, bbox_inches='tight')
    plt.clf()
    plt.show()
