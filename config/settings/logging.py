
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{asctime} - {name} - {levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'method_tracker_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/method_tracker.log',
            'formatter': 'detailed',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'method_tracker': {
            'handlers': ['method_tracker_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
