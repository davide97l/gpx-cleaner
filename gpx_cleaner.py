#!/usr/bin/env python3
import argparse
import datetime

import gpxpy.gpx
from geopy.distance import distance


def run(activity_gpx, min_pause_seconds=1):

    gpx = activity_gpx
    removed = datetime.timedelta()
    last = None
    start = None
    stops = 0
    tot_dist = 0.
    ret_data = {}

    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                time = point.time
                if i == 0:
                    start = time
                time -= removed
                if last is not None:
                    last_point = segment.points[i-1]
                    d = distance((point.latitude, point.longitude), (last_point.latitude, last_point.longitude)).m
                    if time - last >= datetime.timedelta(seconds=min_pause_seconds):
                        print('Pause {}: {}s | {:.3f}m'.format(stops+1, time - last, d))
                        ret_data['Pause {}'.format(stops+1)] = [time - last, d]
                        removed += time - last
                        stops += 1
                    elif d > 10:
                        raise AssertionError('Long distance between points. Handle?')
                    else:
                        tot_dist += d
                if removed > datetime.timedelta():
                    gpx.tracks[0].segments[0].points[i].time = time - removed
                last = time

    print('Elapsed time: {}s'.format(last - start + removed))
    print('Moving time: {}s'.format(last - start))
    print('Paused time: {}s'.format(removed))
    print('Total distance: {:.3f}m'.format(tot_dist/1000.))
    ret_data['Elapsed time'] = last - start + removed
    ret_data['Moving time'] = last - start
    ret_data['Total distance'] = tot_dist/1000.
    ret_data['Paused time'] = removed
    gpx_xml = gpx.to_xml()
    return gpx_xml, ret_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='gpx_cleaner')
    parser.add_argument(
        '--min-pause-seconds',
        default=1,
        type=int,
        help='If the time distance between two time points is larger than this, the track will be split.')
    parser.add_argument(
        'input_file_path',
        help='Input GPX file')
    parser.add_argument(
        'output_file_path',
        help='Output GPX file')
    args = parser.parse_args()

    activity_gpx = '/Users/asommer/Downloads/Zepp20230921114213.gpx'
    gpx_file = open(args.input_file_path, 'r')
    gpx = gpxpy.parse(gpx_file)
    gpx_xml, data = run(gpx, min_pause_seconds=args.min_pause_seconds)
    with open(args.output_file_path, 'w') as f:
        f.write(gpx_xml)
    print('Created {}'.format(args.output_file_path))
