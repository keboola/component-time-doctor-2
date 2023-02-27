ENDPOINT_MAPPING = {
    '_users': {
        'endpoint': '/api/1.0/users',
        'table_name': 'users.csv',
        'pks': ['id'],
        'placeholders': []
    },
    'worklog': {
        'endpoint': '/api/1.0/activity/worklog',
        'table_name': 'worklog.csv',
        'pks': [],
        'placeholders': ['user'],
        'time-window': True
    },
    'timeuse': {
        'endpoint': '/api/1.0/activity/timeuse',
        'table_name': 'timeuse.csv',
        'pks': [],
        'placeholders': ['user'],
        'time-window': True
    },
    'edit-time': {
        'endpoint': '/api/1.0/activity/edit-time',
        'table_name': 'edit_time.csv',
        'pks': [],
        'placeholders': ['user'],
        'time-window': True
    },
    'projects': {
        'endpoint': '/api/1.0/projects',
        'table_name': 'projects.csv',
        'pks': ['id'],
        'placeholders': []
    },
    'tasks': {
        'endpoint': '/api/1.0/tasks',
        'table_name': 'tasks.csv',
        'pks': ['id'],
        'placeholders': []
    }
}
