#!/usr/bin/env python3
import argparse
import datetime

import gpxpy.gpx
from geopy.distance import distance


def run(activity_gpx, min_pause_seconds=1):
    gpx = activity_gpx
    paused = datetime.timedelta()
    moving = datetime.timedelta()
    stops = 0
    tot_dist = 0.
    ret_data = {}

    for track in gpx.tracks:
        segment_index = 0
        while segment_index < len(track.segments):
            segment = track.segments[segment_index]
            last = None
            for point_index, point in enumerate(segment.points):
                time = point.time
                if last is not None:  # did we have a previous point in this segment?
                    last_point = segment.points[point_index-1]
                    d = distance((point.latitude, point.longitude), (last_point.latitude, last_point.longitude)).m
                    if time - last >= datetime.timedelta(seconds=min_pause_seconds):
                        print('Pause {}: {}s | {:.3f}m'.format(stops+1, time - last, d))
                        ret_data['Pause {}'.format(stops+1)] = [time - last, d]
                        paused += time - last
                        stops += 1

                        before_pause, after_pause = segment.split(point_index-1)
                        track.segments[segment_index] = before_pause
                        track.segments.insert(segment_index+1, after_pause)

                        # Continue with next segment (the one we just inserted: `after_pause`)
                        break
                    else:
                        tot_dist += d
                last = time

            moving += track.segments[segment_index].points[-1].time - track.segments[segment_index].points[0].time
            segment_index += 1

    print('Elapsed time: {}s'.format(moving + paused))
    print('Moving time: {}s'.format(moving))
    print('Paused time: {}s'.format(paused))
    print('Total distance: {:.3f}m'.format(tot_dist/1000.))
    ret_data['Elapsed time'] = moving + paused
    ret_data['Moving time'] = moving
    ret_data['Total distance'] = tot_dist/1000.
    ret_data['Paused time'] = paused
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
