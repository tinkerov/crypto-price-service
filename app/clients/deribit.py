import aiohttp

class DeribitClient:
    BASE_URL = "https://www.deribit.com/api/v2/public/get_index_price"

    async def get_index_price(self, ticker: str) -> float:
        params = {"index_name": ticker}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.BASE_URL,
                params=params,
            ) as response:
                response.raise_for_status()
                data = await response.json()

            return float(data["result"]["index_price"])