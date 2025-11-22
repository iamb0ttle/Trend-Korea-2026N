from browser_client import BrowserClient
from crawler import collect_weekly_news_total, collect_weekly_news_economy
from storage import save_news_rows_to_csv

from datetime import date

def main():
  client = BrowserClient()

  try:
    client.login()

    start = date(2025, 1, 1)
    end = date(2025, 11, 21)

    total_rows = collect_weekly_news_total(client, start, end)
    economy_rows = collect_weekly_news_economy(client, start, end)

  finally:
    client.close()

  save_news_rows_to_csv(total_rows, "../datasets/total_news_2025.csv")
  save_news_rows_to_csv(economy_rows, "../datasets/economy_news_2025.csv")
  
if __name__ == "__main__":
  main()