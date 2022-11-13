import re
import sys
from datetime import datetime, timedelta

import requests
import pandas as pd
from lxml import etree


URL = "https://co-ophousingtoronto.coop/resources/find-a-coop/?region=toronto-central&vacancies=both"


if __name__ == "__main__":

    # timing
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    # getting running list of avail coops
    old = pd.read_csv("data.csv").sort_values(by="date")

    # if already checked today, don't alter list
    if old.iloc[-1]["date"] == today:
        print("Already checked today. Exit 0")
        sys.exit(0)

    # getting page for today
    res = requests.get(URL)
    html = res.text

    # parsing for results
    root = etree.HTML(html)
    rows = root.xpath("//div[@class='coop-table']/div[@class='coop-tile']")
    class_pat = re.compile(r"^coop-field (?P<field>[A-z]+)")
    new_data = []
    for row in rows:
        new_data.append({
            "date": today,
            "name": row.xpath("//div[@class='coop-field name']/text()")[0],
            "status": row.xpath("//div[@class='coop-field vacancies']/strong/text()")[0]
        })
    new = pd.DataFrame(new_data)

    # updating current list of coops
    final = pd.concat([old, new]).reset_index(drop=True)
    final.to_csv("data.csv", index=False)
