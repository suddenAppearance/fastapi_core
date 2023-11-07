from httpx import Timeout
from pydantic_settings import BaseSettings


class HTTPXConfig(BaseSettings):
    HTTPX_TIMEOUT: int = 5
    HTTPX_CONNECT_TIMEOUT: int = 5
    HTTPX_READ_TIMEOUT: int = 30
    HTTPX_WRITE_TIMEOUT: int = 5
    HTTPX_POOL_TIMEOUT: int = 5

    def get_timeout(self) -> Timeout:
        return Timeout(
            timeout=self.HTTPX_TIMEOUT,
            connect=self.HTTPX_CONNECT_TIMEOUT,
            read=self.HTTPX_READ_TIMEOUT,
            write=self.HTTPX_WRITE_TIMEOUT,
            pool=self.HTTPX_POOL_TIMEOUT,
        )
