import datetime
import logging
try:
    import threading
except ImportError:
    threading = None

from pyramid_debugtoolbar.panels import DebugPanel
from pyramid_debugtoolbar.utils import format_fname

_ = lambda x: x


class ThreadTrackingHandler(logging.Handler):
    def __init__(self):
        if threading is None:
            raise NotImplementedError(
                "threading module is not available, "
                "the logging panel cannot be used without it")
        logging.Handler.__init__(self)
        self.records = {}  # a dictionary that maps threads to log records

    def emit(self, record):
        self.get_records().append({
            'message': record.getMessage(),
            'time': datetime.datetime.fromtimestamp(record.created),
            'level': record.levelname,
            'file': format_fname(record.pathname),
            'file_long': record.pathname,
            'line': record.lineno,
        })

    def get_records(self, thread=None):
        """
        Returns a list of records for the provided thread, of if none is
        provided, returns a list for the current thread.
        """
        if thread is None:
            thread = threading.currentThread()
        if thread not in self.records:
            self.records[thread] = []
        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]


handler = ThreadTrackingHandler()
logging.root.addHandler(handler)


class LoggingPanel(DebugPanel):
    name = 'logging'
    template = 'pyramid_debugtoolbar.panels:templates/logger.dbtmako'
    title = _('Log Messages')
    nav_title = _('Logging')

    def __init__(self, request):
        handler.clear_records()
        self.data = {'records': []}

    def process_response(self, response):
        records = self.get_and_delete()
        self.data = {'records': records}

    @property
    def has_content(self):
        if self.data.get('records'):
            return True
        else:
            return False

    @property
    def log_level_summary(self):
        """
        returns number of times a logging level is present. Used to allow end
        user to quickly see what types of log records are present.
        """
        summary = dict([('CRITICAL',0),
                        ('ERROR',0),
                        ('WARNING',0),
                        ('INFO',0),
                        ('DEBUG',0),
                        ('NOTSET',0)])
        for r in self.data.get('records'):
            if 'level' in r.keys() and r['level'] in summary.keys():
                #ToDo: Use numeric level to catch custom logging levels.
                summary[r['level']] +=1
        return summary

    def get_highest_log_level(self):
        if self.log_level_summary['CRITICAL'] > 0:
            # showing total counts of critical and error since they are colored the same.
            return ('CRITICAL', self.log_level_summary['CRITICAL'] + self.log_level_summary['ERROR'])
        elif self.log_level_summary['ERROR'] > 0:
            return ('ERROR', self.log_level_summary['ERROR'])
        elif self.log_level_summary['WARNING'] > 0:
            return ('WARNING', self.log_level_summary['WARNING'])
        elif self.log_level_summary['INFO'] > 0:
            return ('INFO', self.log_level_summary['INFO'])
        elif self.log_level_summary['DEBUG'] > 0:
            return ('DEBUG', self.log_level_summary['DEBUG'])
        elif self.log_level_summary['NOTSET'] > 0:
            return ('NOTSET', self.log_level_summary['NOTSET'])
        else:
            return (None, 0) 

    def get_and_delete(self):
        records = handler.get_records()
        handler.clear_records()
        return records

    @property
    def nav_subtitle(self):
        if self.data:
            return '%d' % self.get_highest_log_level()[1]

    @property
    def nav_subtitle_bg_color(self):
        log_level = self.get_highest_log_level()[0]
        if log_level in ('CRITICAL', 'ERROR'):
            return 'progress-bar-danger'
        elif log_level == 'WARNING':
            return 'progress-bar-warning'
        elif log_level == 'INFO':
            return 'progress-bar-info'
        else:
            return ''



def includeme(config):
    config.add_debugtoolbar_panel(LoggingPanel)
