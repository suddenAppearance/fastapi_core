from pydantic_settings import BaseSettings


class ProfilerSettings(BaseSettings):
    PROFILING_ENABLED: bool = True
    PROFILER_INTERVAL: float = 0.001

    PROFILER_QUERY_PARAM: str = "profile_req"
