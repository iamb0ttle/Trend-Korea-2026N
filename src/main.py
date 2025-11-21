from browser_client import BrowserClient

def main():
  client = BrowserClient()

  client.login(screening=True)
  
  client.close()
  
if __name__ == "__main__":
  main()