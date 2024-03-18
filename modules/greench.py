import logging,m3u8,requests
from requests.adapters import HTTPAdapter, Retry

class Greench:
    def __init__(self, username:str, password:str):

        self.api_url = "https://sp.gch.jp/api"
        self.api_epg_url = "https://sp.gch.jp/api_epg"
        self.username = username
        self.password = password
        self.retry_policy = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[ 500, 502, 503, 504 ]
        )
        try:
            res_json = self.login()
            if res_json == None:
                raise Exception("initialize instance failed: failed to login")
            self.at = res_json["at"]
            self.dt = res_json["dt"]
            logging.info(f"initialize instance succeeded: {self.username}")
        except Exception as e:
            logging.error(e)
            raise

    def login(self) -> bool:
        s = requests.Session()
        s.mount('https://', HTTPAdapter(max_retries=self.retry_policy))
        try:
            url = f"{self.api_url}/at"
            response = s.post(
                url=url,
                json={"login_id": self.username, "password": self.password},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                logging.debug(f"greench login succeeded: {self.username}")
                return response.json()
            else:
                logging.warning(f"/at Request error url: {url} response: {response}")
                return None
        except requests.exceptions.RequestException as e:
            logging.warning(f"/at failed: {e}")
            return None

    def get_without_auth(self, url:str, params:dict={}) -> dict|None:
        s = requests.Session()
        s.mount('https://', HTTPAdapter(max_retries=self.retry_policy))
        try:
            response = s.get(
                url=url,
                params=params,
            )
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"Request error url: {url} response: {response}")
                return None
        except requests.exceptions.RequestException as e:
            logging.warning(f"{url} Request failed: url: {url} exception: {e}")
            return None

    def post(self, url:str, obj:dict|None=None) -> dict|None:
        try:
            s = requests.Session()
            s.mount('https://', HTTPAdapter(max_retries=self.retry_policy))
            response = s.post(
                url=url,
                json=obj,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"{self.at}",
                },
            )
            if response.status_code == 200:
                return response.json()
            else:
                logging.warning(f"Request error url: {url} response: {response}")
                return None
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request failed: url: {url} exception: {e}")
            return None

    def get_latest_epg(self, channel_code:str="ch1"):
        return self.get_without_auth(f"{self.api_epg_url}/latest", params={"channel_code": channel_code})

    def get_m3u8(self, pc:str, di:str="1", dgi:str="2", ch:str="ch1", lightviewer:bool=False) -> m3u8.M3U8|None:
        resp = self.post(f"{self.api_url}/vi", obj={"pc": pc, "di": di, "dgi": dgi, "ch": ch, "lightviewer": lightviewer})
        if resp != None:
            return m3u8.loads(content=resp[0]["v"])
        logging.warning(f"failed to /vi response: {resp}")
        return None
