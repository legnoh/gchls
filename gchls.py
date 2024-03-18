import logging,os,sys
from modules.greench import Greench

GCH_EMAIL = os.environ["GCH_EMAIL"]
GCH_PASSWORD = os.environ["GCH_PASSWORD"]
OUTPUT_FILEPATH = os.environ["OUTPUT_FILEPATH"]

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
log_level = os.getenv("LOGLEVEL", logging.INFO)
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=log_level)

if __name__ == '__main__':
    
    logging.info("logged in to GreenCh...")
    gch = Greench(GCH_EMAIL, GCH_PASSWORD)

    logging.info("Fetching latest epg data...")
    epg = gch.get_latest_epg()
    if epg == None:
      logging.error("error with get epg")
      sys.exit(1)

    logging.info("Fetching m3u8 data...")
    m3u8_data = gch.get_m3u8(epg[0][0]["program_code"])
    if m3u8_data == None:
      logging.error("error with get m3u8")
      sys.exit(1)

    logging.info("Parsing m3u8 data...")
    for stream in m3u8_data.playlists:
      if stream.stream_info.average_bandwidth == 3000000:
        m3u8_url = stream.uri

        logging.info(f"exporting url data to {OUTPUT_FILEPATH} ...")
        with open(OUTPUT_FILEPATH, mode='w') as f:
          f.write(f"GCH_STREAM_URL = \"{m3u8_url}\"")
          logging.info("SUCCESS: get url successfully!")
          sys.exit(0)

    logging.error("FAILED: not found active stream url")
    sys.exit(1)
