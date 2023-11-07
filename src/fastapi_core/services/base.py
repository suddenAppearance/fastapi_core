import typing

T = typing.TypeVar("T")


class Context:
    _context: typing.Dict[str, typing.Any]

    def __init__(self, context: typing.Optional[typing.Dict[str, typing.Any]] = None):
        if context is None:
            context = {}
        super().__setattr__("_state", context)

    def __setattr__(self, key: typing.Any, value: typing.Any) -> None:
        self._context[key] = value

    def __getattr__(self, key: typing.Any) -> typing.Any:
        try:
            return self._context[key]
        except KeyError:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, key))

    def __delattr__(self, key: typing.Any) -> None:
        del self._context[key]


class BaseService:
    def __init__(self, context: Context, *args, **kwargs):
        self.context = context
        self.args = args
        self.kwargs = kwargs

    def get_service(self, cls: typing.Type[T]) -> T:
        return cls(self.context, *self.args, **self.kwargs)
