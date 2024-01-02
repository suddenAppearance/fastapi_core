from typing import Any

from httpx import Response

from fastapi_core.settings.app import APISettings


class InterServiceContractMismatchException(Exception):
    def __init__(self, response: Response, errors: Any):
        self.response = response
        self.errors = errors

    def get_detail(self) -> dict[str, Any]:
        detail = {"message": "Contract mismatch"}
        if APISettings().DEBUG:
            try:
                json_body = self.response.json()
            except Exception:
                json_body = None
            detail["cause"] = {
                "url": str(self.response.url),
                "method": self.response.request.method,
                "sent_data": str(self.response.request.content),
                "received_data": str(self.response.content),
                "received_data_pretty": json_body,
                "response_code": self.response.status_code,
                "errors": self.errors,
            }

        return detail
