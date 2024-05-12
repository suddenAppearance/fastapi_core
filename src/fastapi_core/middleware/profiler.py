from fastapi.requests import Request
from pyinstrument import Profiler
from starlette.responses import HTMLResponse

from fastapi_core.settings.profiler import ProfilerSettings

settings = ProfilerSettings()


async def profile_request_middleware(request: Request, call_next):
    profiling = request.query_params.get(settings.PROFILER_QUERY_PARAM, False)
    if profiling:
        profiler = Profiler(interval=settings.PROFILER_INTERVAL, async_mode="enabled")
        profiler.start()
        await call_next(request)
        profiler.stop()
        return HTMLResponse(profiler.output_html())
    else:
        return await call_next(request)
