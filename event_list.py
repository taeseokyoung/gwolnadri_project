import requests, os, django
from bs4 import BeautifulSoup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from events import models

url = "https://www.chf.or.kr/cont/{}/all/month/menu/363?thisPage=1&idx={}&searchCategory1=&searchCategory2={}&searchField=all&searchDate={}&weekSel=&searchText="
view_value = "calendar"
event_value = ""
place_value = "617"
date_value = "202306"
formatted_url = url.format(view_value, event_value, place_value, date_value)
html = requests.get(formatted_url)
soup = BeautifulSoup(html.content, "html.parser")

thumbnail_items = soup.find_all("div", class_="thumb_cont")
event_info = []
for item in thumbnail_items:
    event_title = item.find(class_="tit").text.strip()
    event_date = item.find(class_="thumb_date").text.split(" ~ ")
    event_img = item.find("img")["src"]

    # Add to DB
    models.EventList(
        title=event_title,
        start_date=event_date[0],
        end_date=event_date[1],
        image=event_img,
    ).save()
