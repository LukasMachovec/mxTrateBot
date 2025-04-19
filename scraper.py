from time import sleep
from mxTrateBot import TOKEN, GROUP_ID, LOGIN, PASSWORD
from datetime import datetime
from facebook_scraper import get_posts
import requests
import databaseManager

database = databaseManager.database


def scraper():
    sites = database.sites
    while True:
        for site in sites:
            new_posts = search(site["name"], site["latest_post_time"])
            if len(new_posts) == 0:
                continue
            elif len(new_posts) == 1:
                send_msg(f"Nový příspěvek od {new_posts[0]['name']}\n{new_posts[0]['latest_post_url']}")
                database.update_site(new_posts[0])
            else:
                for i in range(len(new_posts) - 1, -1, -1):
                    send_msg(f"Nový příspěvek od {new_posts[i]['name']}\n{new_posts[i]['latest_post_url']}")
                database.update_site(new_posts[0])
            sleep(60.0 / len(sites))
    assert False


def search(site_name: str, time: str or None) -> list:
    """Looks through five posts that were posted after specified time and returns them.
    The newest post is always at index 0.
    If time is None, function always returns five posts.
    """
    if time is None:
        old_post_time = datetime.min
    else:
        old_post_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    posts = []
    posts_searched = 5
    post_index = 0

    # Searches from the newest to the oldest
    for post in get_posts(site_name, pages=1, credentials=(LOGIN, PASSWORD)):
        if post["time"] > old_post_time:
            posts.append(post)
        post_index += 1
        if post_index == posts_searched:
            break
    if not posts:
        return []
    new_sorted_posts = sorted(posts, key=lambda x: x["time"], reverse=True)

    formatted_posts = []
    for post in new_sorted_posts:
        formatted_posts.append({"name": site_name, "latest_post_time": str(post["time"]),
                                "latest_post_url": post["post_url"]})
    return formatted_posts


def send_msg(text: str):
    token = TOKEN
    chat_id = GROUP_ID
    url_req = "https://api.telegram.org/bot" + str(token) + "/sendMessage" + "?chat_id=" + str(chat_id) + "&text=" + text
    requests.get(url_req)
