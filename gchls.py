import datetime,json,logging,os,zoneinfo
from modules.greench import Greench

GCH_EMAIL = os.environ["GCH_EMAIL"]
GCH_PASSWORD = os.environ["GCH_PASSWORD"]
OUTPUT_FILEPATH = os.environ.get("OUTPUT_FILEPATH", "./urls.tfvars.json")
ORIGIN_TZ = zoneinfo.ZoneInfo("Asia/Tokyo")

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
log_level = os.getenv("LOGLEVEL", logging.INFO)
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=log_level)

streams = {"GCH_STREAMS": []}

if __name__ == '__main__':
    
    logging.info("logged in to GreenCh...")
    gch = Greench(GCH_EMAIL, GCH_PASSWORD)

    for ch in range(1, 6):

      logging.info(f"ch{ch}: Fetching latest epg data...")
      epg = gch.get_latest_epg(channel_code=ch)
      if epg == [] or epg == None:
        logging.info(f"ch{ch}: latest epg data was not found.")
        continue

      start_at = datetime.datetime.strptime(epg[0][0]['live_start_datetime'], "%Y-%m-%d %H:%M:%S").astimezone(ORIGIN_TZ)
      end_at = datetime.datetime.strptime(epg[0][0]['live_end_datetime'], "%Y-%m-%d %H:%M:%S").astimezone(ORIGIN_TZ)
      if start_at - datetime.timedelta(hours=12) > datetime.datetime.now(ORIGIN_TZ):
        logging.warning(f"ch{ch}: this program is too feature program")
        continue

      logging.info(f"ch{ch}: Fetching m3u8 data...")
      m3u8_data = gch.get_m3u8(epg[0][0]["program_code"], ch=ch)
      if m3u8_data == None:
        logging.error(f"ch{ch}: error with get m3u8")
        continue

      logging.info(f"ch{ch}: Parsing m3u8 data...")
      m3u8_url = next((item for item in m3u8_data.playlists if item.stream_info.average_bandwidth == 3000000), None)
      if m3u8_url != None and  hasattr(m3u8_url, 'uri'):
        streams["GCH_STREAMS"].append({
          "channel": f"ch{ch}",
          "program_name": epg[0][0]['program_name'],
          "stream_url": m3u8_url.uri,
          "start_at": start_at.isoformat(),
          "end_at": end_at.isoformat(),
        })
   
    logging.info(f"exporting streams data to {OUTPUT_FILEPATH} ...")

    with open(OUTPUT_FILEPATH, mode='w') as f:
      f.write(json.dumps(streams, indent=2))
      logging.info(f"{ch}: SUCCESS: get url successfully.")
