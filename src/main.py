from browser_client import BrowserClient
from crawler import collect_weekly_news_total, collect_weekly_news_economy

from datetime import date
import json

def main():
  client = BrowserClient()

  client.login()
  
  weekly_news_total_dict = collect_weekly_news_total(client, date(2025, 1, 1), date(2025, 11, 21))
  weekly_news_economy_dict = collect_weekly_news_economy(client, date(2025, 1, 1), date(2025, 11, 21))
  
  client.close()
  
if __name__ == "__main__":
  main()