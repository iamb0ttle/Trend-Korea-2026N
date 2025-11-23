from datetime import date, timedelta, datetime
import sys


def load_stopwords(path: str = "../stopwords/ko_news_stopwords.txt") -> set[str]:
  """
  Loads stopwords from a specified text file.
  
  The file is expected to contain one stopword per line.

  Args:
    path (str): The file path to the text file containing stopwords. 
                Defaults to "../stopwords/ko_news_stopwords.txt".
    
  Returns:
    set[str]: A set of stopwords loaded from the file.
  """
  with open(path, "r", encoding="utf-8") as f:
    # Read each line, strip whitespace, and add to set if not empty
    return {line.strip() for line in f if line.strip()}
      

def generate_fridays(start_date: date, end_date: date) -> list[date]:
  """
  Generates a list of all Fridays between the given start and end dates.
  
  Args:
    start_date (date): The start date object.
    end_date (date): The end date object.
    
  Returns:
    list[date]: A list of date objects representing Fridays found.
  """
  
  # 1. Calculate the first Friday on or after start_date.
  # Mon:0, Tue:1, Wed:2, Thu:3, Fri:4, Sat:5, Sun:6
  # Formula: (target_weekday - current_weekday + 7) % 7
  days_ahead = (4 - start_date.weekday() + 7) % 7
  cur = start_date + timedelta(days=days_ahead)

  fridays = []
  while cur <= end_date:
    fridays.append(cur)
    cur += timedelta(days=7)

  return fridays

def parse_str_to_date(date_str: str) -> date:
  """Helper to convert YYYYMMDD string to date object for CLI input."""
  return datetime.strptime(date_str, "%Y%m%d").date()

def main():
  while True:
    print("\n" * 2)
    print("===========[Utils Test Playground !!]===========")
    print()
    print("SELECT Util want to test!!")  
    print()
    print("1 - Friday Generator: Generates a list of all Fridays between the given start and end dates.")
    print("2 - Stopwords Loader: Loads stopwords from a text file.")
    print("q - Quit Program")
    print()
    
    user_input = input("Your input (number or 'q'): ").strip().lower()

    # Exit condition
    if user_input == 'q':
      print("Exiting program. Goodbye!")
      break

    # Validate numeric input
    if not user_input.isdigit():
      print("[!] Please input a valid number.")
      continue
      
    input_util_num = int(user_input)
    
    # --- Feature 1: Friday Generator ---
    if input_util_num == 1:
      print()
      print("You selected Friday Generator!")
      print()
      print("===========[Friday Generator]===========")
      print()
      
      try:
        # Input is received as string (YYYYMMDD)
        s_input = input("Please input start date (FORMAT: YYYYMMDD e.g 20250101): ")
        e_input = input("Please input end date   (FORMAT: YYYYMMDD e.g 20250101): ")
        
        # Conversion happens OUTSIDE the core logic function
        start_date_obj = parse_str_to_date(s_input)
        end_date_obj = parse_str_to_date(e_input)
        
        # Pass date objects to the function
        result = generate_fridays(start_date_obj, end_date_obj)
        
        print("-" * 40)
        if result:
          print(f"Num of Fridays found: {len(result)}")
          for day in result:
            print(f" - {day}")
        else:
          print("No Fridays found or invalid date range.")
        print("-" * 40)

      except ValueError:
        print("\n[!] Error: Invalid date format. Please use YYYYMMDD.")
        
    # --- Feature 2: Stopwords Loader ---
    elif input_util_num == 2:
      print()
      print("You selected Stopwords Loader!")
      print()
      print("===========[Stopwords Loader]===========")
      print()

      # Updated default path to .txt
      default_path = "../stopwords/ko_news_stopwords.txt"
      path_input = input(f"Input file path (Press Enter to use default: '{default_path}'): ").strip()
      
      target_path = path_input if path_input else default_path

      try:
        stopwords = load_stopwords(target_path)
        print("-" * 40)
        print(f"Successfully loaded {len(stopwords)} stopwords from '{target_path}'.")
        # Sort for better readability in preview
        preview_list = sorted(list(stopwords))
        print(f"Preview (first 5): {preview_list[:5]}")
        print("-" * 40)
      
      except FileNotFoundError:
        print(f"\n[!] Error: File not found at '{target_path}'. Please check the path.")
      except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        
    else:
      print("[!] Unknown selection. Please try again.")

    # Continue Check
    print()
    cont = input("Do you want to continue testing? (Y/n): ").strip().lower()
    if cont == 'n':
      print("Exiting program. Goodbye!")
      break

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("\n\nForced exit. Goodbye!")
    sys.exit(0)