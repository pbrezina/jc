"""jc - JSON CLI output utility lsof Parser

Usage:

    specify --lsof as the first argument if the piped input is coming from lsof

Compatibility:

    'linux'

Examples:

    $ sudo lsof | jc --lsof -p
    [
      {
        "command": "systemd",
        "pid": 1,
        "tid": null,
        "user": "root",
        "fd": "cwd",
        "type": "DIR",
        "device": "253,0",
        "size_off": 224,
        "node": 64,
        "name": "/"
      },
      {
        "command": "systemd",
        "pid": 1,
        "tid": null,
        "user": "root",
        "fd": "rtd",
        "type": "DIR",
        "device": "253,0",
        "size_off": 224,
        "node": 64,
        "name": "/"
      },
      {
        "command": "systemd",
        "pid": 1,
        "tid": null,
        "user": "root",
        "fd": "txt",
        "type": "REG",
        "device": "253,0",
        "size_off": 1624520,
        "node": 50360451,
        "name": "/usr/lib/systemd/systemd"
      },
      ...
    ]

    $ sudo lsof | jc --lsof -p -r
    [
      {
        "command": "systemd",
        "pid": "1",
        "tid": null,
        "user": "root",
        "fd": "cwd",
        "type": "DIR",
        "device": "8,2",
        "size_off": "4096",
        "node": "2",
        "name": "/"
      },
      {
        "command": "systemd",
        "pid": "1",
        "tid": null,
        "user": "root",
        "fd": "rtd",
        "type": "DIR",
        "device": "8,2",
        "size_off": "4096",
        "node": "2",
        "name": "/"
      },
      {
        "command": "systemd",
        "pid": "1",
        "tid": null,
        "user": "root",
        "fd": "txt",
        "type": "REG",
        "device": "8,2",
        "size_off": "1595792",
        "node": "668802",
        "name": "/lib/systemd/systemd"
      },
      ...
    ]
"""
import jc.utils
import jc.parsers.universal


class info():
    version = '1.0'
    description = 'lsof parser'
    author = 'Kelly Brazil'
    author_email = 'kellyjonbrazil@gmail.com'

    # compatible options: linux, darwin, cygwin, win32, aix, freebsd
    compatible = ['linux']


def process(proc_data):
    """
    Final processing to conform to the schema.

    Parameters:

        proc_data:   (dictionary) raw structured data to process

    Returns:

        List of dictionaries. Structured data with the following schema:

        [
          {
            "command":    string,
            "pid":        integer,
            "tid":        integer,
            "user":       string,
            "fd":         string,
            "type":       string,
            "device":     string,
            "size_off":   integer,
            "node":       integer,
            "name":       string
          }
        ]
    """
    for entry in proc_data:
        # integer changes
        int_list = ['pid', 'tid', 'size_off', 'node']
        for key in int_list:
            if key in entry:
                try:
                    key_int = int(entry[key])
                    entry[key] = key_int
                except (ValueError, TypeError):
                    entry[key] = None
    return proc_data


def parse(data, raw=False, quiet=False):
    """
    Main text parsing function

    Parameters:

        data:        (string)  text data to parse
        raw:         (boolean) output preprocessed JSON if True
        quiet:       (boolean) suppress warning messages if True

    Returns:

        dictionary   raw or processed structured data
    """
    if not quiet:
        jc.utils.compatibility(__name__, info.compatible)

    raw_output = []

    linedata = data.splitlines()

    # Clear any blank lines
    cleandata = list(filter(None, linedata))

    if cleandata:
        cleandata[0] = cleandata[0].lower()
        cleandata[0] = cleandata[0].replace('/', '_')

        raw_output = jc.parsers.universal.sparse_table_parse(cleandata)

        '''
        # find column value of last character of each header
        header_text = cleandata.pop(0).lower()

        # clean up 'size/off' header
        # even though forward slash in a key is valid json, it can make things difficult
        header_row = header_text.replace('/', '_')

        headers = header_row.split()

        header_spec = []
        for i, h in enumerate(headers):
            # header tuple is (index, header_name, col)
            header_spec.append((i, h, header_row.find(h) + len(h)))

        # parse lines
        for entry in cleandata:
            output_line = {}

            # normalize data by inserting Null for missing data
            temp_line = entry.split(maxsplit=len(headers) - 1)

            for spec in header_spec:

                index = spec[0]
                header_name = spec[1]
                col = spec[2] - 1     # subtract one since column starts at 0 instead of 1

                if header_name == 'command' or header_name == 'name':
                    continue
                if entry[col] in string.whitespace:
                    temp_line.insert(index, None)

            name = ' '.join(temp_line[9:])
            fixed_line = temp_line[0:9]
            fixed_line.append(name)

            output_line = dict(zip(headers, fixed_line))
            raw_output.append(output_line)
        '''

    if raw:
        return raw_output
    else:
        return process(raw_output)
