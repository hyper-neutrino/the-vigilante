import bs4
import html
import json
import requests
import time
import websocket

retries = 0

while True:
    try:
        ws = websocket.create_connection("wss://qa.sockets.stackexchange.com")
        ws.send("155-questions-active")
        break
    except:
        print(f"Websocket failed to connect. Retry #{retries}.")
        retries += 1
        time.sleep(1)

while True:
    a = ws.recv()
    if a is not None and a != "":
        a = json.loads(a)
        if a["action"] == "hb":
            ws.send("hb")
        elif a["action"] == "155-questions-active":
            data = json.loads(a["data"])
            site = data["apiSiteParameter"]
            id = data["id"]
            r = requests.get(data["ownerUrl"])
            if r.status_code == 200:
                b = bs4.BeautifulSoup(r.text, "html.parser")
                rep = int(b.find_all("div", {"class": "fs-body3 fc-dark"})[0].getText().replace(",", ""))
                if rep > 100:
                    print(data["ownerDisplayName"], f"has more than 100 reputation ({rep}), so their post has been skipped.")
                    continue
            r = requests.get(f"https://api.stackexchange.com/2.3/posts/{id}?site={site}&filter=!6VvPDzP5s)iW2")
            if r.status_code != 200:
                print(f"Could not fetch post on {site} with id {id} - {r.status_code}")
                continue
            try:
                data = r.json()["items"][0]
            except:
                print(f"Failed to fetch post on {site} with id {id} - it might have been deleted")
                continue
            print("POST HAS BEEN FOUND. TYPE:", data["post_type"].upper())
            print("AUTHOR:", data["ownerDisplayName"], "with", rep, "reputation")
            print("-" * 80)
            print(html.unescape(data["body_markdown"]))
            print("=" * 80)
