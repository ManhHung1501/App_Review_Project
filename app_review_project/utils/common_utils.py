from datetime import datetime

def parse_appstore_dates(record):
    attributes = record['attributes']
    attributes['date'] = datetime.strptime(attributes['date'], "%Y-%m-%dT%H:%M:%SZ")
    if 'developerResponse' in attributes:
        attributes['developerResponse']['modified'] = datetime.strptime(attributes['developerResponse']['modified'], "%Y-%m-%dT%H:%M:%SZ")
    return record