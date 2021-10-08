from pprint import pprint
import asyncio
import aiohttp
from datetime import datetime as dt
from seleniumwire import webdriver


class DextoolsAPI:
    def __init__(self):
        self._base_url = "https://www.dextools.io"
        self._pair_addr = "0x921ae85c25550a39b80b9a55f70bc364e8c44c1c"
        self._pair_url = f"{self._base_url}/app/ether/pair-explorer/{self._pair_addr}"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-using')
        self.options.add_argument("--full-screen")
        self.options.add_argument("disable-notifications")
        self.options.add_argument('--disable-logging')
        self.options.add_argument('--remote-debugging-port=9230')
        self.options.add_argument('--disable-setuid-sandbox')
        self._driver = webdriver.Chrome(
            executable_path="/usr/bin/chromedriver", options=self.options)
        self._driver.request_interceptor = self.interceptor
        self._headers = None
        self._driver.get(self._pair_url)
        # assert self._headers is not None
        self._session = None
        print('Browser loaded!')

    def interceptor(self, request):
        print('New request')
        token = request.headers["Authorization"]
        if token is not None and token != "Bearer null":
            print('Headers found!')
            print(self._headers)
            self._headers = request.headers

    async def get_latest_pirce(self):
        while not self._headers:
            await asyncio.sleep(0.5)
            print('No headers')

        if self._session is None:
            self._session = aiohttp.ClientSession()
        URL = f'{self._base_url}/chain-ethereum/api/uniswap/1/pairexplorer?v=1.19.0&pair={self._pair_addr}&ts={dt.now().timestamp()}-0'
        async with self._session.get(URL, headers=self._headers) as response:
            res = await response.json()
            return res


async def main():
    api = DextoolsAPI()
    data = await api.get_latest_pirce()
    pprint(data)
    print(data["result"][-1]["price"])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
