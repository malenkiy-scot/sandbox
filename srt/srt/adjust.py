"""
Adjust subtitles in an .srt file to a given timing

If only the first timestamp is specified all timestamps in the .srt file are moved by the same offset.

If both the first and the last timestamps are specified the timestamps are 'stretched' or 'shortened' to fit
"""

__author__ = 'malenkiy_scot'

import re


def convert_srt_timestamp(timestamp_str):
    """
    Convert SRT timestamp to ms

    :param timestamp_str: SRT timestamp as string
    :return: timestamp in ms
    """

    timestamp_regex = re.compile(r'(\d\d):(\d\d):(\d\d),(\d\d\d)')
    _match = timestamp_regex.match(timestamp_str)
    return int(_match.group(1))*3600*1000 + int(_match.group(2))*60*1000 + int(_match.group(3))*1000 + int(_match.group(4))


def convert_ms_to_srt_timestamp(ms):
    """
    Convert time in ms to SRT timestamp

    :param ms: time in ms
    :return:  time as SRT timestamp
    """
    ms = int(ms)

    h = ms / 3600000
    ms -= h * 3600 * 1000
    m = ms / 60000
    ms -= m * 60 * 1000
    s = ms / 1000
    ms -= s*1000

    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def parse_args():
    """Parse command-line parameters"""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-i', '--first-index',
                        metavar='FIRST_SUBTITLE_INDEX',
                        type=int,
                        default=1,
                        required=False,
                        dest='first_index',
                        help="first timestamp refers to this subtitle; defaults to 1")

    parser.add_argument('first_timestamp',
                        metavar='FIRST_TIMESTAMP',
                        type=convert_srt_timestamp,
                        help="first timestamp, required")

    parser.add_argument('-I', '--last-index',
                        metavar='LAST_SUBTITLE_INDEX',
                        type=int,
                        default=-1,
                        required=False,
                        dest='last_index',
                        help="last timestamp refers to this subtitle; defaults to the last subtitle")

    parser.add_argument('-l', '--last-timestamp',
                        metavar='LAST_TIMESTAMP',
                        required=False,
                        default=None,
                        dest='last_timestamp',
                        type=convert_srt_timestamp,
                        help="last timestamp")

    parser.add_argument('srt_file',
                        metavar='SRT_FILE',
                        help=".srt file to process")

    return vars(parser.parse_args())


if __name__ == '__main__':
    _args = parse_args()

    subtitles = []
    subtitle_regex = re.compile(r'(\d\d:\d\d:\d\d,\d\d\d)\s*-->\s*(\d\d:\d\d:\d\d,\d\d\d)')

    with open(_args['srt_file'], 'r') as srt_file:
        index = 0
        while True:
            line = srt_file.readline()
            if len(line) == 0:
                break
            if len(line) == 1:
                continue
            line = line.strip()

            index += 1
            _index = int(line)
            assert(index == _index)

            line = srt_file.readline().strip()
            match = subtitle_regex.match(line)

            ts1 = convert_srt_timestamp(match.group(1))
            ts2 = convert_srt_timestamp(match.group(2))

            subtitle_content = srt_file.readline().strip()

            subtitles.append((index, ts1, ts2, subtitle_content))

    if _args['last_index'] == -1:
        _args['last_index'] = len(subtitles) + 1

    if _args['last_timestamp'] is None:
        _args['last_timestamp'] = subtitles[_args['last_index'] - 1][1]

    first_timestamp_index = _args['first_index']
    first_timestamp_ms = _args['first_timestamp']
    last_timestamp_index = _args['last_index']
    last_timestamp_ms = _args['last_timestamp']

    shift = first_timestamp_ms - subtitles[first_timestamp_index - 1][1]
    stretch = 1.0
    if _args['last_timestamp'] is not None:
        stretch = (last_timestamp_ms - first_timestamp_ms)\
                  / float(subtitles[last_timestamp_index - 1][1] - subtitles[first_timestamp_index - 1][1])

    new_subtitles = []
    with open(_args['srt_file'] + '.new', 'w') as srt_file:
        for subtitle in subtitles:
            (index, ts1, ts2, subtitle_content) = subtitle
            ts1 = (ts1 + shift - first_timestamp_ms) * stretch + first_timestamp_ms
            ts2 = (ts2 + shift - first_timestamp_ms) * stretch + first_timestamp_ms

            srt_file.writelines(['%d\n' % index,
                                 '%s --> %s\n' % (convert_ms_to_srt_timestamp(ts1), convert_ms_to_srt_timestamp(ts2)),
                                 subtitle_content,
                                 '\n\n',
                                 ])
