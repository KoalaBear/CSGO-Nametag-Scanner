import json
import re
from math import ceil
from time import sleep

import requests
from bs4 import BeautifulSoup


class Settings:
    URL = ""  # E.g: https://steamcommunity.com/market/listings/730/Glock-18%20%7C%20Weasel%20%28Field-Tested%29
    AMOUNT_PER_PAGE = 100
    DELAY_WHEN_BLOCKED = 30
    STEAM_CURRENCY = 1  # 1: USD


class ListingsPageIds:
    RESULTS_TABLE_ID = "searchResultsRows"


class MarketScraper:
    @staticmethod
    def _build_url(start_index, per_page=Settings.AMOUNT_PER_PAGE, currency=Settings.STEAM_CURRENCY):
        return Settings.URL + f"?query=&start={start_index}" \
                              f"&count={per_page}" \
                              f"&currency={currency}"

    @staticmethod
    def _get_page(page_url):
        """Returns an item page soup, cooked with the Settings class consts and a given start_index param"""
        page = requests.get(page_url)
        while page.status_code == 429:
            sleep(Settings.DELAY_WHEN_BLOCKED)
            page = requests.get(page_url)
        soup = BeautifulSoup(page.content, "html.parser")
        if soup.select("#searchResultsTable > div.market_listing_table_message"):
            return None
        return soup

    @staticmethod
    def _find_assets(page_soup) -> dict:
        p = re.compile(r'var g_rgAssets = {"730":{"2":(.*)}};')
        for script in page_soup.find_all("script", {"src": False}):
            assets_code = p.findall(script.string)
            if assets_code:
                return json.loads(assets_code[0])

    @staticmethod
    def _find_nametags(assets):
        for id, item in assets.items():
            if item.get("fraudwarnings"):
                print(f"CUSTOM NAME FOUND! {item['fraudwarnings']}")

    @staticmethod
    def scan_nametags(amount=1000, per_page=100, start_index=0):
        pages_to_scan = ceil(amount / per_page)
        for page in range(pages_to_scan):
            print(f"---------------------------------PAGE {page}/{pages_to_scan}--------------------------------------")
            page_url = MarketScraper._build_url(start_index, per_page=per_page)
            print(f"\t\t URL: {page_url}")
            page = MarketScraper._get_page(page_url)
            if not page:
                print("Reached last page of listings the item")
                return
            assets = MarketScraper._find_assets(page)
            MarketScraper._find_nametags(assets)
            start_index += per_page


if __name__ == '__main__':
    pass
    # MarketScraper.scan_nametags(amount=10000, per_page=100, start_index=20000)
