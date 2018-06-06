#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/6 11:05
# @Author  : zhuo_hf@foxmail.com
# @Site    :
# @File    : xxx.py
# @Software: PyCharm
import re
from datetime import datetime

# BEGIN entity

class LogInfoType(object):
    DEBUG = "D"
    VERBOSE = "I"
    WARNING = "W"
    ERROR = "E"
    UNKNOWN = "U"

class LogLine(object):
    def __init__(self):
        self.datetime = datetime.min
        self.logger_pid = 0
        self.logger_tid = 0
        self.info_type = LogInfoType.UNKNOWN
        self.event = None

class PssLogLine(LogLine):
    EVENT_NAME = "am_pss"

    def __init__(self):
        super(PssLogLine, self).__init__()
        self.event = PssLogLine.EVENT_NAME
        self.process_pid = 0
        self.process_uid = -1
        self.process_name = None
        self.pss = 0
        self.uss = 0
        self.swap = 0

class ProcessDiedLogLine(LogLine):
    EVENT_NAME = "am_proc_died"

    def __init__(self):
        super(ProcessDiedLogLine, self).__init__()
        self.event = ProcessDiedLogLine.EVENT_NAME
        self.process_uid = -1
        self.process_pid = 0
        self.process_name = None

class KillLogLine(LogLine):
    EVENT_NAME = "am_kill"

    def __init__(self):
        super(KillLogLine, self).__init__()
        self.event = KillLogLine.EVENT_NAME
        self.process_uid = -1
        self.process_pid = 0
        self.process_name = None
        self.oom_score_adj = -1
        self.reason = None

class WakeLockAcquiringLogLine(LogLine):
    EVENT_NAME = "pm_wakelock_acquire"

    def __init__(self):
        super(WakeLockAcquiringLogLine, self).__init__()
        self.event = WakeLockAcquiringLogLine.EVENT_NAME
        self.lock = 0
        self.flags = None
        self.tag = None
        self.process_pid = 0
        self.process_uid = -1

class WakeLockReleasingLogLine(LogLine):
    EVENT_NAME = "pm_wakelock_release"

    def __init__(self):
        super(WakeLockReleasingLogLine, self).__init__()
        self.event = WakeLockReleasingLogLine.EVENT_NAME
        self.lock = 0
        self.tag = None
        self.flags = None

class ScreenOnLogLine(LogLine):
    EVENT_NAME = "dic_screenon"

    def __init__(self):
        super(ScreenOnLogLine, self).__init__()
        self.event = self.EVENT_NAME
        self.screenOn = None

# END entity
# BEGIN filter

class Filter(object):
    _DEFAULT_YEAR = 2017
    DAY_PARAM = "day"
    MONTH_PARAM = "month"
    HOUR_PARAM = "hour"
    MINUTE_PARAM = "minute"
    SECOND_PARAM = "second"
    MILLIS_PARAM = "millis"
    LOGGER_PID_PARAM = "logger_pid"
    LOGGER_TID_PARAM = "logger_tid"
    INFO_TYPE_PARAM = "info_type"

    SPACE_MASK = "\s*"
    DATETIME_MASK = r"(?P<%s>\d{2})-(?P<%s>\d{2})" % (MONTH_PARAM, DAY_PARAM)+ \
        SPACE_MASK + \
        r"(?P<%s>\d{2}):(?P<%s>\d{2}):(?P<%s>\d{2})\.(?P<%s>\d{3})" % (HOUR_PARAM, \
            MINUTE_PARAM, SECOND_PARAM, MILLIS_PARAM)
    LOGGER_MASK = r"(?P<%s>\d+)" % (LOGGER_PID_PARAM)+ \
        SPACE_MASK + \
        r"(?P<%s>\d+)" % (LOGGER_TID_PARAM) + \
        SPACE_MASK + \
        r"(?P<%s>.{1})" % (INFO_TYPE_PARAM)

    def __init__(self):
        self._compiled = None
        self._last_evaluation = None

    def _join_masks(self, masks):
        return Filter.SPACE_MASK.join(masks)

    def _get_datetime(self, match):
        if match:
            gdic = match.groupdict()
            return datetime(Filter._DEFAULT_YEAR, \
                int(gdic[Filter.MONTH_PARAM]), int(gdic[Filter.DAY_PARAM]), \
                int(gdic[Filter.HOUR_PARAM]), int(gdic[Filter.MINUTE_PARAM]), \
                int(gdic[Filter.SECOND_PARAM]), int(gdic[Filter.MILLIS_PARAM]))
        return None

    def _get_logger_pid(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[Filter.LOGGER_PID_PARAM])
        return None

    def _get_logger_tid(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[Filter.LOGGER_TID_PARAM])
        return None

    def _get_info_type(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[Filter.INFO_TYPE_PARAM]
        return None

    def _get_log_line(self, instance, match):
        instance.datetime = self._get_datetime(match)
        instance.logger_pid = self._get_logger_pid(match)
        instance.logger_tid = self._get_logger_tid(match)
        instance.info_type = self._get_info_type(match)

    def eval(self, line):
        if not self._compiled:
            return False

        self._last_evaluation = self._compiled.match(line)

        return self._last_evaluation is not None

    def get_log_line(self):
        return None

#PssFilter继承于Filter
class PssFilter(Filter):
    PSS_EVENT_NAME = "am_pss"
    PSS_EVENT_PARAM = "am_pss"
    PROCESS_PID_PARAM = "process_pid"
    PROCESS_UID_PARAM = "process_uid"
    PROCESS_NAME_PARAM = "process_name"
    PSS_PARAM = "pss"
    USS_PARAM = "uss"
    SWAP_PARAM = "swap"

    PSS_MASK = r"(?P<%s>%s)" % (PSS_EVENT_PARAM, PSS_EVENT_NAME) + \
        Filter.SPACE_MASK + \
        r":" + Filter.SPACE_MASK + \
        r"\[(?P<%s>\d+),(?P<%s>\d+),(?P<%s>.*),(?P<%s>\d+),(?P<%s>\d+),(?P<%s>\d+)\]" % \
            (PROCESS_PID_PARAM, PROCESS_UID_PARAM, \
            PROCESS_NAME_PARAM, PSS_PARAM, USS_PARAM, SWAP_PARAM)

    def __init__(self):
        super(PssFilter, self).__init__()
        self._compiled = re.compile(self._join_masks([ \
            Filter.DATETIME_MASK, Filter.LOGGER_MASK, PssFilter.PSS_MASK]))

    def _get_process_pid(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[PssFilter.PROCESS_PID_PARAM])
        return None

    def _get_process_uid(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[PssFilter.PROCESS_UID_PARAM])
        return None

    def _get_process_name(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[PssFilter.PROCESS_NAME_PARAM]
        return None

    def _get_pss(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[PssFilter.PSS_PARAM])
        return None

    def _get_uss(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[PssFilter.USS_PARAM])
        return None

    def _get_swap(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[PssFilter.SWAP_PARAM])
        return None

    def _get_log_line(self, instance, match):
        super(PssFilter, self)._get_log_line(instance, match)
        instance.process_pid = self._get_process_pid(match)
        instance.process_uid = self._get_process_uid(match)
        instance.process_name = self._get_process_name(match)
        instance.pss = self._get_pss(match)
        instance.uss = self._get_uss(match)
        instance.swap = self._get_swap(match)

    def get_log_line(self):
        pss_log_line = PssLogLine()
        self._get_log_line(pss_log_line, self._last_evaluation)
        return pss_log_line

class ProcessDiedFilter(Filter):
    PROC_DIED_EVENT_NAME = "am_proc_died"
    PROC_DIED_PARAM = "am_proc_died"
    PROCESS_UID_PARAM = "process_uid"
    PROCESS_PID_PARAM = "process_pid"
    PROCESS_NAME_PARAM = "process_name"

    PROC_DIED_MASK = r"(?P<%s>%s)" % (PROC_DIED_PARAM, PROC_DIED_EVENT_NAME) + \
        Filter.SPACE_MASK + r":" + Filter.SPACE_MASK + \
        r"\[(?P<%s>\d+),(?P<%s>\d+),(?P<%s>.+)\]" % \
        (PROCESS_UID_PARAM, PROCESS_PID_PARAM, PROCESS_NAME_PARAM)

    def __init__(self):
        super(ProcessDiedFilter, self).__init__()
        self._compiled = re.compile(self._join_masks([Filter.DATETIME_MASK, \
            Filter.LOGGER_MASK, ProcessDiedFilter.PROC_DIED_MASK]))

    def _get_process_uid(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[ProcessDiedFilter.PROCESS_UID_PARAM])
        return None

    def _get_process_pid(self, match):
        if match:
            gdic = match.groupdict()
            return int(gdic[ProcessDiedFilter.PROCESS_PID_PARAM])
        return None

    def _get_process_name(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[ProcessDiedFilter.PROCESS_NAME_PARAM]
        return None

    def _get_log_line(self, instance, match):
        super(ProcessDiedFilter, self)._get_log_line(instance, match)
        instance.process_uid = self._get_process_uid(match)
        instance.process_pid = self._get_process_pid(match)
        instance.process_name = self._get_process_name(match)

    def get_log_line(self):
        process_died_log_line = ProcessDiedLogLine()
        self._get_log_line(process_died_log_line, self._last_evaluation)
        return process_died_log_line

class KillFilter(Filter):
    KILL_EVENT_NAME = "am_kill"
    KILL_EVENT_PARAM = "am_kill"
    PROCESS_UID_PARAM = "process_uid"
    PROCESS_PID_PARAM = "process_pid"
    PROCESS_NAME_PARAM = "process_name"
    OOM_SCORE_ADJ_PARAM = "oom_score_adj"
    REASON_PARAM = "reason"

    KILL_MASK = r"(?P<%s>%s)" % (KILL_EVENT_PARAM, KILL_EVENT_NAME) + \
        Filter.SPACE_MASK + r":" + Filter.SPACE_MASK + \
        r"\[(?P<%s>\d),(?P<%s>\d),(?P<%s>.+),(?P<%s>\d),(?P<%s>.*)\]" % (PROCESS_UID_PARAM, \
            PROCESS_PID_PARAM, PROCESS_NAME_PARAM, OOM_SCORE_ADJ_PARAM, REASON_PARAM)

    def __init__(self):
        super(KillFilter, self).__init__()
        self._compiled = re.compile(self._join_masks([
            Filter.DATETIME_MASK, Filter.LOGGER_MASK, KillFilter.KILL_MASK
        ]))

    def _get_process_uid(self, match):
        if match:
            gdic = match.groupdic()
            return gdic[KillFilter.PROCESS_UID_PARAM]
        return None

    def _get_process_pid(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[KillFilter.PROCESS_PID_PARAM]
        return None

    def _get_process_name(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[KillFilter.PROCESS_NAME_PARAM]
        return None

    def _get_oom_score_adj(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[KillFilter.OOM_SCORE_ADJ_PARAM]
        return None

    def _get_reason(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[KillFilter.REASON_PARAM]
        return None

    def _get_log_line(self, instance, match):
        super(KillFilter, self)._get_log_line(instance, match)
        instance.process_uid = self._get_process_uid(match)
        instance.process_pid = self._get_process_pid(match)
        instance.process_name = self._get_process_name(match)
        instance.oom_score_adj = self._get_oom_score_adj(match)
        instance.reason = self._get_reason(match)

    def get_log_line(self):
        kill_log_line = KillLogLine()
        self._get_log_line(kill_log_line, self._last_evaluation)
        return kill_log_line

class WakeLockAcquiringFilter(Filter):
    LOCK_PARAM = "lock"
    FLAGS_PARAM = "flags"
    TAG_PARAM = "tag"
    UID_PARAM = "process_uid"
    PID_PARAM = "process_pid"
    WAKELOCK_MASK = r"PowerManagerService:" + Filter.SPACE_MASK + \
        r"acquireWakeLockInternal:" + Filter.SPACE_MASK + \
        r"lock=(?P<%s>\d+)" % (LOCK_PARAM) + "," + Filter.SPACE_MASK + \
        r"flags=(?P<%s>0x\d+)" % (FLAGS_PARAM) + "," + Filter.SPACE_MASK + \
        r"tag=\"(?P<%s>.+)\"" % (TAG_PARAM) + "," + Filter.SPACE_MASK + \
        r".*uid=(?P<%s>\d+),\s*pid=(?P<%s>\d+)" % (UID_PARAM, PID_PARAM)

    def __init__(self):
        super(WakeLockAcquiringFilter, self).__init__()
        self._compiled = re.compile(self._join_masks([Filter.DATETIME_MASK,
            Filter.LOGGER_MASK, WakeLockAcquiringFilter.WAKELOCK_MASK]))

    def _get_lock(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.LOCK_PARAM]
        return None

    def _get_process_uid(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.UID_PARAM]
        return None

    def _get_process_pid(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.PID_PARAM]
        return None

    def _get_tag(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.TAG_PARAM]
        return None

    def _get_flags(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.FLAGS_PARAM]
        return None

    def _get_log_line(self, instance, match):
        super(WakeLockAcquiringFilter, self)._get_log_line(instance, match)
        instance.tag = self._get_tag(match)
        instance.lock = self._get_lock(match)
        instance.flags = self._get_flags(match)
        instance.process_pid = self._get_process_pid(match)
        instance.process_uid = self._get_process_uid(match)

    def get_log_line(self):
        wl_logline = WakeLockAcquiringLogLine()
        self._get_log_line(wl_logline, self._last_evaluation)
        return wl_logline

class WakeLockReleasingFilter(Filter):
    LOCK_PARAM = "lock"
    TAG_PARAM = "tag"
    FLAGS_PARAM = "flags"
    WAKELOCK_MASK = r".*releaseWakeLockInternal:\s*" + \
        r"lock=(?P<%s>\d+)\s+\[(?P<%s>.+)\], flags=(?P<%s>0x\d+)" % (LOCK_PARAM, \
            TAG_PARAM, FLAGS_PARAM)

    def __init__(self):
        super(WakeLockReleasingFilter, self).__init__()
        self._compiled = re.compile(self._join_masks([
            self.DATETIME_MASK, self.LOGGER_MASK, self.WAKELOCK_MASK
        ]))

    def _get_lock(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.LOCK_PARAM]
        return None

    def _get_tag(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.TAG_PARAM]
        return None

    def _get_flags(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.FLAGS_PARAM]
        return None

    def _get_log_line(self, instance, match):
        super(WakeLockReleasingFilter, self)._get_log_line(instance, match)
        instance.lock = self._get_lock(match)
        instance.tag = self._get_tag(match)
        instance.flags = self._get_flags(match)

    def get_log_line(self):
        wl_logline = WakeLockReleasingLogLine()
        self._get_log_line(wl_logline, self._last_evaluation)
        return wl_logline

class ScreenOnFilter(Filter):
    SCREENON_PARAM = "screen_on"
    SCREENON_MASK = r"updateDisplayLocked:\s+screenOn=(?P<%s>(true|false))" % (SCREENON_PARAM)

    def __init__(self):
        super(ScreenOnFilter, self).__init__()
        self._compiled = re.compile(self._join_masks([
            self.DATETIME_MASK, self.LOGGER_MASK, self.SCREENON_MASK
        ]))

    def _get_screen_on(self, match):
        if match:
            gdic = match.groupdict()
            return gdic[self.SCREENON_PARAM]
        return None

    def _get_log_line(self, instance, match):
        super(ScreenOnFilter, self)._get_log_line(instance, match)
        instance.screen_on = self._get_screen_on(match)

    def get_log_line(self):
        screenon_logline = ScreenOnLogLine()
        self._get_log_line(screenon_logline, self._last_evaluation)
        return screenon_logline

# END filter
# BEGIN collection

class LogLineCollection(object):
    def __init__(self, log_line_items=None):
        self._log_line_items = list() if log_line_items is None else log_line_items
        self._core_filter_collection = list()

    def add_core_filter(self, core_filter):
        self._core_filter_collection.append(core_filter)

    def add_log(self, log_text):
        for core_filter in self._core_filter_collection:
            if core_filter.eval(log_text):
                self._log_line_items.append(core_filter.get_log_line())
                break

    def add_log_in_batch(self, log_text_collection):
        for log_text in log_text_collection:
            self.add_log(log_text)

    def _is_instance_of(self, item, item_type_list, default=True):
        if item_type_list:
            for item_type in item_type_list:
                if isinstance(item, item_type):
                    return True
            return False
        return default

    def get_log_line_items(self, item_type_list=None):
        return [item for item in self._log_line_items if self._is_instance_of(item, item_type_list)]

    @staticmethod
    def instance(core_filters):
        log_line_collection = LogLineCollection()
        for core_filter in core_filters:
            log_line_collection.add_core_filter(core_filter)

        return log_line_collection

# END collection