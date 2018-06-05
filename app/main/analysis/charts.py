import plotly #plotly是开挂的作图神器
import plotly.graph_objs as go
from itertools import groupby
from .core import PssLogLine, ProcessDiedLogLine, KillLogLine, LogLineCollection, \
    WakeLockAcquiringLogLine, WakeLockReleasingLogLine
from datetime import timedelta, datetime

# BEGIN DATA_BUILDER

class PssDataTimedLine(object):
    def __init__(self, datetime, pss, uss, swap):
        self.datetime = datetime
        self.pss = pss
        self.uss = uss
        self.swap = swap

    def create_new(self, datetime, pss, uss, swap):
        return PssDataTimedLine(datetime, \
            self.pss + pss, \
            self.uss + uss, \
            self.swap + swap)

    def create_from_item(self, item):
        return self.create_new(item.datetime, \
            item.pss, item.uss, item.swap)

    def remove_new(self, datetime, pss, uss, swap):
        return PssDataTimedLine(datetime, \
            self.pss - pss, \
            self.uss - uss, \
            self.swap - swap)

    def remove_from_item(self, item):
        return self.remove_new(item.datetime, \
            item.pss, item.uss, item.swap)

    @staticmethod
    def create_null():
        return PssDataTimedLine(None, 0, 0, 0)

class PssDataBuilder(object):
    @staticmethod
    def group_by_processes(log_line_collection):
        items = sorted(log_line_collection.get_log_line_items([PssLogLine]), \
            key=lambda item: item.process_name)

        return groupby(items, lambda item: item.process_name)

    @staticmethod
    def summarize(log_line_collection):
        items = sorted(log_line_collection.get_log_line_items([PssLogLine, \
            ProcessDiedLogLine, KillLogLine]), \
            key=lambda item: item.datetime)

        if items:
            data = list()
            pids = dict()
            current = PssDataTimedLine.create_null()

            for item in items:
                if isinstance(item, PssLogLine):
                    if item.process_pid in pids:
                        old_item = pids[item.process_pid]
                        current = current.remove_from_item(old_item)
                    current = current.create_from_item(item)
                    pids[item.process_pid] = item
                    data.append(current)
                elif isinstance(item, KillLogLine) or isinstance(item, ProcessDiedLogLine):
                    pid = item.process_pid
                    if pid in pids:
                        current = current.remove_from_item(pids[pid])
                        del pids[pid]
                        data.append(current)

            return data
        return None

    @staticmethod
    def summarize_per_process(log_line_collection):
        items = sorted(log_line_collection.get_log_line_items([PssLogLine, \
            ProcessDiedLogLine, KillLogLine]), \
            key=lambda item: item.datetime)

        if items:
            items = sorted(items, key=lambda item: item.process_name)
            grouped = groupby(items, key=lambda item: item.process_name)
            mapping = dict()

            for key, group in grouped:
                mapping[key] = PssDataBuilder.summarize(LogLineCollection(group))

            return mapping
        return None

import time
from datetime import timedelta
from datetime import datetime

class WakeLockTagTrace(object):
    def __init__(self):
        self.tag = None
        self.datetimes = list()
        self.usages = list()
        self.labels = list()

    def datetimes_and_texts_filtered(self):
        i = 0
        res = list()
        tex = list()
        while i < len(self.usages) and i < len(self.datetimes):
            if self.usages[i]:
                res.append(self.datetimes[i])
                tex.append(self.labels[i])
            else:
                res.append(self.datetimes[i])
                tex.append(self.labels[i])
                res.append(None)
                tex.append(None)
            i += 1
        return res, tex

    def tags(self, size):
        tlist = list()

        i = 0
        while i < size:
            tlist.append(self.tag)
            i += 1

        return tlist

class WakeLockDataBuilder(object):
    @staticmethod
    def lines(log_line_collection):
        items = sorted(log_line_collection.get_log_line_items([
            WakeLockReleasingLogLine, WakeLockAcquiringLogLine
        ]), key=lambda item: item.tag)

        traces = list()

        for key, values in groupby(items, key=lambda item: item.tag):
            tagtrace = WakeLockTagTrace()
            tagtrace.tag = key

            nitems = sorted(values, key=lambda nitem: nitem.datetime)

            for nitem in nitems:
                if isinstance(nitem, WakeLockAcquiringLogLine):
                    tagtrace.datetimes.append(nitem.datetime)
                    tagtrace.usages.append(True)
                    tagtrace.labels.append(str(nitem.lock))
                elif isinstance(nitem, WakeLockReleasingLogLine):
                    tagtrace.datetimes.append(nitem.datetime)
                    tagtrace.usages.append(False)
                    tagtrace.labels.append(str(nitem.lock))
            traces.append(tagtrace)
        return traces

# END DATA_BUILDER
# BEGIN CHART_BUILDER

class PssChartBuilder(object):
    @staticmethod
    def generate_plot_chart(log_line_collection):
        data = list()
        grouped = PssDataBuilder.group_by_processes(log_line_collection)

        for key, group in grouped:
            pss_x_values = [item.pss for item in group]
            trace = go.Box(
                x = pss_x_values,
                name = key
            )

            data.append(trace)

        plotly.offline.plot(data, filename="pss_box_plot_" + str(datetime.today()))

    @staticmethod
    def generate_timed_line(log_line_collection):
        items = PssDataBuilder.summarize(log_line_collection)

        items = sorted(items, key=lambda item: item.datetime)

        x_axis = [item.datetime for item in items]

        trace_pss = go.Scatter(
            x = x_axis,
            y = [item.pss for item in items],
            name = "pss"
        )
        trace_uss = go.Scatter(
            x = x_axis,
            y = [item.uss for item in items],
            name = "uss"
        )
        trace_swap = go.Scatter(
            x = x_axis,
            y = [item.swap for item in items],
            name = "swap"
        )
        trace_all = go.Scatter(
            x = x_axis,
            y = [item.pss + item.swap for item in items],
            name = "pss + swap"
        )

        data = [trace_pss, trace_uss, trace_swap, trace_all]

        plotly.offline.plot(data, filename="pss_line_chart_system_" + str(datetime.today()))

    @staticmethod
    def generate_timed_line_per_process(log_line_collection):
        itemsdict = PssDataBuilder.summarize_per_process(log_line_collection)
        data = list()

        for key, items in itemsdict.iteritems():
            items = sorted(items, key=lambda item: item.datetime)
            x_axis = [item.datetime for item in items]
            y_axis = [item.pss for item in items]
            trace = go.Scatter(
                x = x_axis,
                y = y_axis,
                name = key
            )

            data.append(trace)

        plotly.offline.plot(data, filename="pss_line_chart_process_" + str(datetime.today()))

class WakeLockChartBuilder(object):
    @staticmethod
    def lines(log_line_collection):
        traces = WakeLockDataBuilder.lines(log_line_collection)
        plotly_traces = list()

        for trace in traces:
            xaxis, texts = trace.datetimes_and_texts_filtered()

            plotly_trace = go.Scatter(
                x = xaxis,
                y = trace.tags(len(xaxis)),
                name = trace.tag,
                text = texts,
                showlegend=False
            )

            plotly_traces.append(plotly_trace)

        layout = go.Layout(
            yaxis = dict(
                showticklabels=True
            )
        )

        fig = go.Figure(data=plotly_traces, layout=layout)
        plotly.offline.plot(fig, filename="wakelock_line_chart_" + str(datetime.today()))


# END CHART_BUILDER