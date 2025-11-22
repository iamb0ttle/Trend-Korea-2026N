import time
from datetime import date, datetime
from typing import Literal, List, Dict, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from browser_client import BrowserClient
from logger import AppLogger
from utils import generate_fridays

WEEKEND_NEWS_URL = "https://www.bigkinds.or.kr/v2/news/weekendNews.do"

Category = Literal["total", "economy"]

logger = AppLogger("[Crawler]")

def _go_to_weekend_news_page(client: BrowserClient, category: Category) -> None:
  """
  Navigate to the weekly issue news page.
  """
  logger.info(f"Navigating to weekend news page. Category: {category}")
  
  d = client.driver
  
  # 1. Access URL
  try:
    logger.debug(f"Accessing URL: {WEEKEND_NEWS_URL}")
    d.get(WEEKEND_NEWS_URL)
    time.sleep(2)
    logger.info("URL access succeeded.")
  except Exception:
    logger.exception("URL access failed.")
    raise

  # 2. Select Category
  try:
    logger.debug("Locating 'issueCategory' select element.")
    select_el = Select(d.find_element(By.ID, "issueCategory"))
    
    if category == "total":
      value = "전체"
    elif category == "economy":
      value = "002000000"
    else:
      raise ValueError(f"Unknown category: {category}")
    
    logger.debug(f"Selecting category value: {value} ({category})")
    select_el.select_by_value(value)
    time.sleep(0.5)
    logger.info("Category selection completed.")
  except Exception:
    logger.exception("Failed to select issue category.")
    raise


def _search_by_date(client: BrowserClient, target_date: date) -> None:
  """
  Input the target date into the search field and submit.
  """
  d = client.driver
  ds = target_date.strftime("%Y-%m-%d")
  logger.info(f"Searching weekend news for anchor date: {ds}")

  try:
    # 1. Wait for Input Element
    logger.debug("Waiting for 'weekend-search-date' input to be clickable.")
    input_el = WebDriverWait(d, 10).until(
      EC.element_to_be_clickable((By.ID, "weekend-search-date"))
    )

    # 2. Focus on Input
    input_el.click()
    time.sleep(0.2)

    # 3. Clear Existing Value
    logger.debug("Clearing existing date value.")
    input_el.send_keys(Keys.CONTROL, "a")
    input_el.send_keys(Keys.DELETE)
    time.sleep(0.1)

    # 4. Input Target Date
    logger.debug(f"Inputting date string: {ds}")
    input_el.send_keys(ds)
    time.sleep(0.2)

    # 5. Click Search Button
    logger.debug("Clicking search button.")
    search_btn = d.find_element(By.CSS_SELECTOR, "button.search-btn")
    search_btn.click()
    
    time.sleep(10)
    logger.info("Search triggered successfully.")

  except Exception:
    logger.exception("Failed during date search process.")
    raise


def _scrape_visible_block(client: BrowserClient, category: Category) -> List[Dict]:
  """
  Parse the visible 5-day blocks (Mon-Fri) on the current screen.
  Includes logic to prevent StaleElementReferenceException.
  """
  d = client.driver
  results = []

  # 1. Identify Container & Count Items
  try:
    logger.debug("Locating result container and counting items.")
    container = WebDriverWait(d, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, "div#weekend-news-result > ul.weekendNews-lst"))
    )
    items_count = len(container.find_elements(By.CSS_SELECTOR, "div.item"))
    logger.debug(f"Found {items_count} day items.")
  except Exception:
    logger.exception("Failed to locate container or count items.")
    return []

  # 2. Iterate Through Items
  for i in range(items_count):
    try:
      # Refresh elements to prevent StaleElementReferenceException
      container = d.find_element(By.CSS_SELECTOR, "div#weekend-news-result > ul.weekendNews-lst")
      day_items = container.find_elements(By.CSS_SELECTOR, "div.item")
      
      if i >= len(day_items):
        break
      
      day_item = day_items[i]
      
      # Extract Date
      date_str = day_item.get_attribute("data-date")
      if not date_str:
        continue

      # 3. Process Inner News List (li)
      li_elements = day_item.find_elements(By.CSS_SELECTOR, "div.cont > ul > li")
      limit = min(len(li_elements), 10)
      
      for j in range(limit):
        try:
          # Refresh li element for safety
          li = li_elements[j]

          a_tag = li.find_element(By.CSS_SELECTOR, "a.topic-row")
          title_attr = a_tag.get_attribute("title") or ""
          title_span = a_tag.find_element(By.TAG_NAME, "span").text.strip()
          title = title_attr if title_attr else title_span

          num_text = a_tag.find_element(By.CSS_SELECTOR, "i.num").text.strip()
          
          try:
            article_count = int(num_text)
          except ValueError:
            article_count = None

          results.append({
            "date": date_str,
            "category": category,
            "title": title,
            "article_count": article_count,
          })
        except Exception:
          logger.warning(f"Failed to parse li element at index {j} of date {date_str}. Skipping.")
          continue

    except Exception:
      logger.exception(f"Error processing day_item index {i}.")
      continue

  logger.info(f"Scraped {len(results)} items (category={category}).")
  return results


def collect_weekly_news_total(
  client: BrowserClient,
  start_date: date,
  end_date: date,
) -> List[Dict]:
  """
  Collect 'Total' category weekly news within the date range.
  """
  logger.info(f"Collecting weekly [Total] news from {start_date} to {end_date}.")

  _go_to_weekend_news_page(client, "total")
  
  fridays = generate_fridays(start_date, end_date)
  all_rows = []

  for fri in fridays:
    anchor_str = fri.strftime("%Y-%m-%d")
    logger.info(f"Processing block anchored at {anchor_str}.")

    try:
      _search_by_date(client, fri)
      block_rows = _scrape_visible_block(client, category="total")

      for row in block_rows:
        d_obj = datetime.strptime(row["date"], "%Y-%m-%d").date()
        if start_date <= d_obj <= end_date:
          all_rows.append(row)
    except Exception:
      logger.exception(f"Failed to process week anchored at {anchor_str}. Skipping to next.")
      continue

  logger.info(f"Finished [Total] collection. Total rows: {len(all_rows)}")
  return all_rows


def collect_weekly_news_economy(
  client: BrowserClient,
  start_date: date,
  end_date: date,
) -> List[Dict]:
  """
  Collect 'Economy' category weekly news within the date range.
  """
  logger.info(f"Collecting weekly [Economy] news from {start_date} to {end_date}.")

  _go_to_weekend_news_page(client, "economy")
  
  fridays = generate_fridays(start_date, end_date)
  all_rows = []

  for fri in fridays:
    anchor_str = fri.strftime("%Y-%m-%d")
    logger.info(f"Processing economy block anchored at {anchor_str}.")

    try:
      _search_by_date(client, fri)
      block_rows = _scrape_visible_block(client, category="economy")

      for row in block_rows:
        d_obj = datetime.strptime(row["date"], "%Y-%m-%d").date()
        if start_date <= d_obj <= end_date:
          all_rows.append(row)
    except Exception:
      logger.exception(f"Failed to process week anchored at {anchor_str}. Skipping to next.")
      continue

  logger.info(f"Finished [Economy] collection. Total rows: {len(all_rows)}")
  return all_rows