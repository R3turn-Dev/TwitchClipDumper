import argparse
import multiprocessing
import os
import pickle
import traceback
from datetime import datetime
from os.path import exists, getsize

import requests

parser = argparse.ArgumentParser(description="Download Twitch clips.")
parser.add_argument("channel", nargs="?", help="Channel ID")
parser.add_argument("--client-id", nargs="?", help="Client ID")
parser.add_argument("--token", nargs="?", help="OAuth2 Authorization token")

VALID_FILENAME = lambda s: "".join(x for x in s if (x.isalnum() or x in "~!@#$%^&()_-+=[]{}.,"))


def main(channel, client_id, token):
    clips = []

    _cursor, _len, _data = fetcher(channel, client_id, token)
    clips += _data

    while _len > 0:
        _cursor, _len, _data = fetcher(channel, client_id, token, pagination=_cursor)
        clips += _data

        if _cursor == "" or _data[-1]["views"] < 10:
            break

    print(len(clips), "clips found.")

    pickle_name = f"clips-{channel}.pkl"
    pickle.dump(clips, open(pickle_name, "wb"))
    print(f"Exported clips data as a pickle file '{pickle_name}'")

    downloading = [
        (
            channel, c['title'],
            int(datetime.strptime(c['created_at'], "%Y-%m-%dT%H:%M:%SZ").timestamp()),
            c['curator']['name'] if c['curator']['name'] == c['curator']['display_name'] else
            c['curator']['display_name'] + f"({c['curator']['name']})",
            c['tracking_id'], c['slug']
            ) for c in clips
        ]

    open(f"urls-{channel}.txt", "w", encoding="UTF-8").write(
        "\n".join([
            VALID_FILENAME(f"{channel}-{c[-1]}-{c[0]}-{c[1]}.mp4") for c in downloading
            ])
        )

    if not channel in os.listdir(os.getcwd()):
        os.mkdir(channel)

    pool = multiprocessing.Pool(min(16, multiprocessing.cpu_count()))
    try:
        pool.map(_isolated_downloader, downloading)
    except KeyboardInterrupt:
        pool.close()


def _isolated_downloader(a):
    channel, title, time, naming, tracking, slug = a

    try:
        fname = VALID_FILENAME(f"{title}-{slug}.mp4")
        path = f"{channel}/{fname}"
        if exists(path) and getsize(path) > 1024:
            print("Ignoring {} due to exist".format(naming))
            return

        req = requests.get("https://clips-media-assets2.twitch.tv/AT-cm%7C" + tracking + ".mp4")
        if len(req.content) < 1024:
            req = requests.get("https://clips-media-assets2.twitch.tv/" + str(tracking) + ".mp4")
            if len(req.content) < 1024:
                print("Empty response", title, naming, tracking)
                # return

        open(f"{channel}/{fname}", "wb").write(req.content)
        os.utime(f"{channel}/{fname}", (time, time))

    except:
        print("Error on", title, naming, tracking, traceback.format_exc())


def fetcher(channel, client_id, token, pagination: str = None):
    resp = requests.get(
        "https://api.twitch.tv/kraken/clips/top?channel={channel}&period=all&limit=100".format(channel=channel)
        + ("" if not pagination else "&cursor=" + pagination)
        ,
        headers={
            "Accept": "vnd.twitchtv.v5+json",
            "Authorization": "Bearer " + token,
            "Client-ID": client_id
            }
        )

    data = resp.json()
    print(len(data["clips"]), data["_cursor"], data["clips"][0]["slug"], data["clips"][-1]["views"])

    return data["_cursor"], len(data["clips"]), data["clips"]


if __name__ == "__main__":
    args = parser.parse_args()

    channel = args.channel
    cid = args.client_id
    token = args.token

    if not (channel and cid and token):
        print("Not enough args")
        exit(-1)

    main(channel, cid, token)
