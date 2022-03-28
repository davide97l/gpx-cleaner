import streamlit as st
import math
import gpxpy
from gpx_cleaner import run
import datetime


def get_pace(dist, time, mile=False):
    # convert datetime to sec
    if not mile:
        pace = (time/dist)/60.*1000.
    else:
        pace = (time/dist)/60.*1609.32
    pace_min = math.floor(pace)
    pace_sec = round((pace % 1) * 60)
    if (pace % 1) * 60 > 59.5:
        pace_min += 1
        pace_sec = 0
    return pace_min, pace_sec


def td_to_str(td):
    td = datetime.datetime.strptime(str(td), "%H:%M:%S")
    if td.hour != 0:
        td = td.strftime('%Hh %Mm %Ss')
    else:
        td = td.strftime('%Mm %Ss')
    td = td.replace(' 0', ' ')
    if td[0] == '0':
        td = td[1:]
    return td


def show():

    st.write("👉 How frequently it happens that your running or cycling activities are **interrupted** by a red traffic light,"
             " the need to drink some water, or simply to wait your partner to reach you? 🤔")
    st.write("👉 Even if you pause your watch during your activity, thus not recording any distance, it will still continue to record your total time"
             " which will be then showed as your **elapsed time** in your application such as Strava. However, Strava"
             " will count this time instead than your **moving time** to compute your Personal Records and the Segments"
             " leaderboard, thus showing a time longer than what your real effort was.")
    st.write("👉 The goal of this application is to **modify** the **gpx file** of your activity such to make the elapsed"
             " time coincide with your moving time while leaving all the other data unchanged. You will then be able to"
             " download your new gpx file and upload it on Strava or in your desired platform.")
    st.write("👉 Feel free to report any bug or suggestion on [Github](https://github.com/davide97l/running-performance-calculator) and leave a ⭐ if you found it useful.")
    st.write("⚠️ Currently are only supported GPX files whose GPS synchronization frequency is exactly 1 second.")

    gpx_file_raw = st.file_uploader("📂 Upload your activity.gpx file", type=["gpx"], accept_multiple_files=False)
    if gpx_file_raw is not None:

        gpx_file = gpxpy.parse(gpx_file_raw)
        gpx_xlm, data = run(gpx_file)

        data_keys = data.keys()
        stop_keys = [key for key in data_keys if 'Pause ' in key]

        #st.write("Uploaded file: **{}**".format(gpx_file_raw.name))
        activity_name = gpx_file_raw.name.split('.')[0] + '_clean.gpx'
        st.write("⏸️ Paused the watch **{}** times:".format(len(stop_keys)))
        for i in range(len(stop_keys)):
            print(data[stop_keys[i]])
            st.write("- ⏸️ Pause {}: **{}**".format(i+1, td_to_str(data[stop_keys[i]][0])))
        st.write("⌛ Elapsed time: **{}** ➡️ **{}**".format(td_to_str(data['Elapsed time']),
                                                           td_to_str(data['Moving time'])))
        st.write("🏃 Moving time: **{}**".format(td_to_str(data['Moving time'])))
        st.write("⏸ Paused time: **{}** ➡️ **0s**".format(td_to_str(data['Paused time'])))
        st.write("🛣️ Total distance: **{:.3f}m**".format(data['Total distance']))

        st.download_button(
            label="📂 Download clean GPX file",
            data=gpx_xlm,
            file_name=activity_name,
        )


if __name__ == "__main__":
    show()
