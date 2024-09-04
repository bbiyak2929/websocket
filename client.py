import httpx

class ExternalServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_example(self, params: dict = None):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/example", params=params)
            response.raise_for_status()  # 에러 발생 시 예외를 던집니다.
            return response.json()
