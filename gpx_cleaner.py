import gpxpy.gpx
import datetime
from geopy.distance import distance


def run(activity_gpx):

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
                    if time - last > datetime.timedelta(seconds=1):
                        print('Pause {}: {}s | {:.3f}m'.format(stops+1, time - last, d))
                        ret_data['Pause {}'.format(stops+1)] = [time - last, d]
                        removed += time - last
                        stops += 1
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
    activity_gpx = 'gpx/activity_177944060.gpx'
    gpx_file = open(activity_gpx, 'r')
    gpx = gpxpy.parse(gpx_file)
    activity_name = activity_gpx.split('.')[0] + '_clean.gpx'
    gpx_xml, data = run(gpx)
    with open(activity_name, 'w') as f:
        f.write(gpx_xml)
    print('Created {}'.format(activity_name))
