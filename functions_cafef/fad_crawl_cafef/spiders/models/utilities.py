# -*- coding: utf-8 -*-

def log_settings(spiderName, log_level, log_formatter=None):
    """`log_levels`: str. Can be one of these: CRITICAL, ERROR, WARNING, INFO, DEBUG
    """
    if log_formatter:
        return {
        'LOG_ENABLED': True,
        'LOG_FILE': f'logs/{spiderName}_log_verbose.log',
        'LOG_LEVEL': log_level,
        'LOG_FORMATTER': log_formatter
    }
    else:
        return {
            'LOG_ENABLED': True,
            'LOG_FILE': f'logs/{spiderName}_log_verbose.log',
            'LOG_LEVEL': log_level
        }
