#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/6 11:05
# @Author  : zhuo_hf@foxmail.com
# @Site    : 
# @File    : utils.py
# @Software: PyCharm
from .core import PssFilter, LogLineCollection, ProcessDiedFilter, KillFilter, \
    WakeLockAcquiringFilter, WakeLockReleasingFilter
from .charts import PssChartBuilder, WakeLockChartBuilder

def pss_chart(infile, box_plot, line_system, line_process):
    log_line_collection = LogLineCollection.instance([
        PssFilter(), ProcessDiedFilter(), KillFilter()
    ])

    lines = infile.readlines()
    new_lines = [line.decode('utf-8') for line in lines]
    log_line_collection.add_log_in_batch(new_lines)
    return PssChartBuilder.generate_timed_line_per_process(log_line_collection)

    #根据参数选择画三种不同的图
    #if box_plot:
    #    PssChartBuilder.generate_plot_chart(log_line_collection)
    #if line_system:
    #    PssChartBuilder.generate_timed_line(log_line_collection)
    #if line_process:
    #    PssChartBuilder.generate_timed_line_per_process(log_line_collection)


#画wakelock
def wakelock_line_chart_process(infile):
    log_line_collection = LogLineCollection.instance([
        WakeLockAcquiringFilter(), WakeLockReleasingFilter()
    ])

    lines = infile.readlines()
    log_line_collection.add_log_in_batch(lines)
    WakeLockChartBuilder.lines(log_line_collection)