import json
from urllib.parse import urlsplit

HISTORY_SCHEMA = [
    # (field name, field type, required, min_value, max_value)
    ('url', str, True, 0, 2048),
    ('start_time', int, True, 2 ** 29, 2 ** 32),  # year 1987-2106
    ('duration', int, False, 0, 1000 * 3600 * 24),  # max 1 day in ms
]


def check_field(value, type_, min_value, max_value):
    if not isinstance(value, type_):
        return None

    if (type_ in (int, float) and
            not (min_value <= value < max_value)):
        value = None
    elif (type_ is str and
          not (min_value <= len(value) < max_value)):
        value = None

    return value


def json_encode(data):
    return json.dumps(
        data, separators=(',', ':'), sort_keys=True).encode('utf-8')


def validate(data):
    if (not isinstance(data, dict) or
            'sessions' not in data or
            not isinstance(data['sessions'], list)):
        return

    sessions = []
    for entry in data['sessions']:
        if not isinstance(entry, dict):
            continue

        missing_field = False
        validated_entry = {}
        for field, type_, required, min_value, max_value in HISTORY_SCHEMA:
            value = check_field(entry.get(field), type_, min_value, max_value)

            if required and not value:
                missing_field = True
                break

            validated_entry[field] = value

        if not missing_field:
            filtered_entry = filter_entry(validated_entry)
            if filtered_entry:
                sessions.append(filtered_entry)

    output = {}
    if sessions:
        output['sessions'] = sessions

    return output


def filter_entry(entry):
    url_result = urlsplit(entry['url'])
    if url_result.username or url_result.password:
        return None

    return entry


def upload_data(task, user, data):
    key = ('user_%s' % user).encode('ascii')
    output = json_encode(data)
    task.cache.set(key, output, ex=3600)
    return True


def main(task, user, payload, _upload_data=True):
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return False

    parsed_data = validate(data)
    if not parsed_data:
        return False

    # Testing hooks.
    if not _upload_data:
        return True

    if _upload_data is True:  # pragma: no cover
        _upload_data = upload_data

    return _upload_data(task, user, parsed_data)