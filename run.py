import os
import argparse
import requests
import pickle
import traceback
from datetime import datetime

parser = argparse.ArgumentParser(description="Download Twitch clips.")
parser.add_argument("channel", nargs="?", help="Channel ID")
parser.add_argument("--client-id", nargs="?", help="Client ID")
parser.add_argument("--token", nargs="?", help="OAuth2 Authorization token")

VALID_FILENAME = lambda s: "".join(x for x in s if (x.isalnum() or x in "~!@#$%^&()_-+=[]{}.,"))


def main(channel, client_id, token):
    clips = []

    _cursor, _len, _data = fetcher(channel, client_id, token)
    clips += _data

    while _len == 100:
        _cursor, _len, _data = fetcher(channel, client_id, token, pagination=_cursor)
        clips += _data

    print(len(clips), "clips found.")

    pickle_name = f"clips-{channel}.pkl"
    pickle.dump(clips, open(pickle_name, "wb"))
    print(f"Exported clips data as a pickle file '{pickle_name}'")

    downloading = [
        (
            c['title'],
            int(datetime.strptime(c['created_at'], "%Y-%m-%dT%H:%M:%SZ").timestamp()),
            c['curator']['name'] if c['curator']['name'] == c['curator']['display_name'] else
            c['curator']['display_name'] + f"({c['curator']['name']})",
            f"https://clips-media-assets2.twitch.tv/AT-cm%7C{c['tracking_id']}.mp4"
        ) for c in clips
    ]

    open(f"urls-{channel}.txt", "w", encoding="UTF-8").write(
        "\n".join([
            VALID_FILENAME(f"{channel}-{c[0]}-{c[1]}.mp4") for c in downloading
        ])
    )

    if not channel in os.listdir(os.getcwd()):
        os.mkdir(channel)

    for title, time, naming, uri in downloading:
        try:
            fname = VALID_FILENAME(f"{title}-{naming}.mp4")

            req = requests.get(uri)
            if req.content:
                open(f"{channel}/{fname}", "wb").write(req.content)

                os.utime(f"{channel}/{fname}", (time, time))

            else:
                print("Empty response", title, naming, uri)

        except:
            print("Error on", title, naming, uri, traceback.format_exc())


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
