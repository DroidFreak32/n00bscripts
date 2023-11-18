#!/usr/bin/env python3

# This is a makeshift python script to parse all the media file's mkvinfo JSON and identify tracks from the media that are not required, to save space.
# Expected input is a json file containing mkvmerge --identification-format json --identify outputs of each file in the media library in a file: mkvinfos.json
# Then the tracks are parsed and ONLY the Track IDs of the required audio/subtitle tracks are selected.
# Next it generates an mkvmerge command for each file, containing the required track IDs. This is saved as a script that can be run to rip only the required media tracks and save it in the destination.
# This has a lot of HARDCODED PATHS!!
# 

import copy
import json
import os,ast
import re
import subprocess
import sys
import urllib.parse

if __name__ == "__main__":

    results = []

    all_sub_codecs = []
    all_sub_names = []
    all_audio_codecs = []
    all_audio_names = []
    rejected_tracks = []

    # List that will contain all the movies with only the required Track IDs
    movies=[]
    # For debugging, also store ALL metadata of all movies as well.
    raw_movies=[]
    # Collect track info from the library
    for line in open('/Users/russhah/Movies/mkvinfos_mini.json', 'r'):

        subtitles=[]
        audios=[]



        movie_info=json.loads(line)
        raw_movies.append(movie_info)
        movie_name=movie_info['file_name']
        movie_tracks=movie_info['tracks']
        for track in movie_tracks:

            keep_sub = False
            keep_aud = False

            if track['type'] == "subtitles":
                sub_name = None

                subtitle_codec = track['codec']
                all_sub_codecs.append(subtitle_codec)

                subtitle_tid = track['id']

                subtitle_language = track['properties']['language']

                if 'track_name' in track['properties'].keys():
                    sub_name = track['properties']['track_name']
                    all_sub_names.append(sub_name)
                    # I don't need commentary tracks
                    if 'commentary' in sub_name.casefold():
                        keep_sub = False
                        rejected_tracks.append(track)
                        continue

                # I only want English Subs
                if (subtitle_language == 'eng' or subtitle_language == 'und'):
                    keep_sub = True


                if keep_sub:
                    subtitles.append(
                        {
                            'id': subtitle_tid,
                            'codec': subtitle_codec,
                            'language': subtitle_language,
                            'name': sub_name
                        }
                    )
                else:
                    rejected_tracks.append(track)

            if track['type'] == "audio":
                audio_name = None

                audio_codec = track['codec']
                all_audio_codecs.append(audio_codec)

                audio_tid = track['id']
                audio_language = track['properties']['language']

                if 'track_name' in track['properties'].keys():
                    audio_name = track['properties']['track_name']
                    all_audio_names.append(audio_name)
                    # I don't need commentary tracks
                    if 'commentary' in audio_name.casefold():
                        keep_aud = False
                        rejected_tracks.append(track)
                        continue

                # Change this to jpn for Animes or else you have a place reserved in hell :) .
                if (audio_language == 'eng' or audio_language == 'und'):
                    keep_aud = True

                if keep_aud:
                    audios.append(
                        {
                            'id': audio_tid,
                            'codec': audio_codec,
                            'language': audio_language,
                            'name': audio_name
                        }
                    )
                else:
                    rejected_tracks.append(track)



        movies.append(
            {
                'name': movie_name,
                'audios': audios,
                'subtitles': subtitles,
                'rawInfo': movie_info
            }
        )


    multi_audio_movies = []

    for movie in movies:
        name = os.path.basename(movie['name'])
        subtitles_len = len(movie['subtitles'])
        audio_len = len(movie['audios'])
        if audio_len > 1:
            multi_audio_movies.append(movie)

        print(
            f"Movie: {name}" \
            "\nAudio Track(s):")
        for i in range(audio_len):
            print(
                f"\t{movie['audios'][i]['codec']} - {movie['audios'][i]['language']}"
                )

        if subtitles_len > 0:
            print(f"Subtitle Tracks:")
            for i in range(subtitles_len):
                print(
                    f"\t{movie['subtitles'][i]['codec']} - {movie['subtitles'][i]['language']}"
                    )

        print("\n\n=================================\n")


    print("\n\nThese Movies have MuliAudio\n")
    for movie in multi_audio_movies:

        name = os.path.basename(movie['name'])
        print(
            f"\n\nMovie: {name}" \
            "\nAudio Track(s):")
        for i in range(len(movie['audios'])):
            print(
                f"\t{movie['audios'][i]['codec']} - {movie['audios'][i]['language']}"
                )

    # Now generating the mkvmerge commands
    # mkvmerge -o $dst_path -a tn1,tn2 -s tn1,tn2 $src_path
    for movie in movies:
        src_path = movie['name']
        dst_path = 'DESTINATION/' + re.sub('.mp4$', '.mkv', movie['name'])

        subtitles_len = len(movie['subtitles'])
        audio_len = len(movie['audios'])

        if movie in multi_audio_movies:
            track_ids = []
            for audio_track in movie['audios']:
                track_ids.append(audio_track['id'])
            audio_tids = ','.join(map(str,track_ids))
        else:
            audio_tids = movie['audios'][0]['id']

        mkvmerge_audio = f"-a {audio_tids}"

        if len(movie['subtitles']) > 0:
            if len(movie['subtitles']) > 1:
                track_ids = []
                for sub_track in movie['subtitles']:
                    track_ids.append(sub_track['id'])
                sub_tids = ','.join(map(str,track_ids))
            else:
                sub_tids = movie['subtitles'][0]['id']

            mkvmerge_subs = f"-s {sub_tids}"
        else:
            mkvmerge_subs = f""

        if ( audio_len + subtitles_len == len(movie['rawInfo']['tracks']) -1):
            cmd = f"mkdir -p \"{os.path.dirname(dst_path)}\"; mv -v \"{src_path}\" \"{dst_path}\""
        else:
            cmd = f"mkvmerge -o \"{dst_path}\" {mkvmerge_audio} {mkvmerge_subs} \"{src_path}\""

        # print(cmd)
        with open("/tmp/mkvscript2.sh", "a+") as outfile:
            outfile.write(cmd + "\n")
