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


class ServiceUnavailableException(Exception):
    """
    Exception Class for raising 503 when gateway returned unexpected response code
    """

    def __init__(self, response: Response, expected_code: list[int]):
        self.response = response
        self.expected_code = expected_code

    def get_log_message(self) -> str:
        """
        Standard log message for failed ext request
        """
        return (
            f"Request to {self.response.url} failed with unexpected status code"
            f" - {self.response.status_code} (expected: {', '.join(str(i) for i in self.expected_code)})"
        )

    def get_detail(self) -> dict[str, Any]:
        """
        Standard detail response for failed ext request
        """
        detail = {"message": "Service unavailable"}
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
                "expected_code": self.expected_code,
                "received_code": self.response.status_code,
            }

        return detail
