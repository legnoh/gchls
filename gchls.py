import base64,logging,m3u8,os,sys,time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service

GCH_EMAIL = os.environ["GCH_EMAIL"]
GCH_PASSWORD = os.environ["GCH_PASSWORD"]
OUTPUT_FILEPATH = os.environ["OUTPUT_FILEPATH"]

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
log_level = os.getenv("LOGLEVEL", logging.INFO)
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=log_level)

if __name__ == '__main__':

  logging.info("initializing selenium...")
  options = webdriver.SafariOptions()
  driver = webdriver.Safari(service=Service(), options=options)
  driver.implicitly_wait(10)

  try:
    logging.info("access to top page -> login page...")
    driver.get("https://sp.gch.jp/")
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, "a#login_page").click()

    logging.info("type email/password -> submit...")
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, 'input#uid').send_keys(GCH_EMAIL)
    driver.find_element(By.CSS_SELECTOR, 'input#passcd').send_keys(GCH_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'input[type=submit]').click()

    logging.info("get stream url in m3u data...")
    time.sleep(3)
    video_tag = driver.find_element(By.CSS_SELECTOR, "video#player_html5_api")
    video_blob_base64 = video_tag.get_attribute("src").strip("data:application/x-mpegURL;base64,")
    video_m3u8 = base64.b64decode(video_blob_base64).decode()
    m3u8_datas = m3u8.loads(content=video_m3u8)
    for stream in m3u8_datas.playlists:
      if stream.stream_info.average_bandwidth == 3000000:
        m3u8_url = stream.uri

        logging.info(f"exporting url data to {OUTPUT_FILEPATH} ...")
        with open(OUTPUT_FILEPATH, mode='w') as f:
          f.write(f"GCH_STREAM_URL = \"{m3u8_url}\"")
          logging.info("SUCCESS: get url successfully!")
          driver.quit()
          sys.exit(0)

    logging.error("FAILED: not found active stream url")
    driver.quit()
    sys.exit(1)

  except NoSuchElementException as e:
    logging.warning(f"FAILED: element not found: {e}")
    driver.quit()
    sys.exit(1)
  
  except TimeoutException as e:
    logging.warning(f"FAILED: timeout occurred: {e}")
    driver.quit()
    sys.exit(1)
