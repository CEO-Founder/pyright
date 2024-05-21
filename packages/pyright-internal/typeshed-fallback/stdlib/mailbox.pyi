import email.message
import io
import sys
from _typeshed import StrPath, SupportsNoArgReadline, SupportsRead
from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from types import TracebackType
from typing import IO, Any, AnyStr, Generic, Literal, Protocol, TypeVar, overload
from typing_extensions import Self, TypeAlias

if sys.version_info >= (3, 9):
    from types import GenericAlias

__all__ = [
    "Mailbox",
    "Maildir",
    "mbox",
    "MH",
    "Babyl",
    "MMDF",
    "Message",
    "MaildirMessage",
    "mboxMessage",
    "MHMessage",
    "BabylMessage",
    "MMDFMessage",
    "Error",
    "NoSuchMailboxError",
    "NotEmptyError",
    "ExternalClashError",
    "FormatError",
]

_T = TypeVar("_T")
_MessageT = TypeVar("_MessageT", bound=Message)

class _SupportsReadAndReadline(SupportsRead[bytes], SupportsNoArgReadline[bytes], Protocol): ...

_MessageData: TypeAlias = email.message.Message | bytes | str | io.StringIO | _SupportsReadAndReadline

class _HasIteritems(Protocol):
    def iteritems(self) -> Iterator[tuple[str, _MessageData]]: ...

class _HasItems(Protocol):
    def items(self) -> Iterator[tuple[str, _MessageData]]: ...

linesep: bytes

class Mailbox(Generic[_MessageT]):
    _path: str  # undocumented
    _factory: Callable[[IO[Any]], _MessageT] | None  # undocumented
    @overload
    def __init__(self, path: StrPath, factory: Callable[[IO[Any]], _MessageT], create: bool = True) -> None: ...
    @overload
    def __init__(self, path: StrPath, factory: None = None, create: bool = True) -> None: ...
    @abstractmethod
    def add(self, message: _MessageData) -> str: ...
    @abstractmethod
    def remove(self, key: str) -> None: ...
    def __delitem__(self, key: str) -> None: ...
    def discard(self, key: str) -> None: ...
    @abstractmethod
    def __setitem__(self, key: str, message: _MessageData) -> None: ...
    @overload
    def get(self, key: str, default: None = None) -> _MessageT | None: ...
    @overload
    def get(self, key: str, default: _T) -> _MessageT | _T: ...
    def __getitem__(self, key: str) -> _MessageT: ...
    @abstractmethod
    def get_message(self, key: str) -> _MessageT: ...
    def get_string(self, key: str) -> str: ...
    @abstractmethod
    def get_bytes(self, key: str) -> bytes: ...
    # As '_ProxyFile' doesn't implement the full IO spec, and BytesIO is incompatible with it, get_file return is Any here
    @abstractmethod
    def get_file(self, key: str) -> Any: ...
    @abstractmethod
    def iterkeys(self) -> Iterator[str]: ...
    def keys(self) -> list[str]: ...
    def itervalues(self) -> Iterator[_MessageT]: ...
    def __iter__(self) -> Iterator[_MessageT]: ...
    def values(self) -> list[_MessageT]: ...
    def iteritems(self) -> Iterator[tuple[str, _MessageT]]: ...
    def items(self) -> list[tuple[str, _MessageT]]: ...
    @abstractmethod
    def __contains__(self, key: str) -> bool: ...
    @abstractmethod
    def __len__(self) -> int: ...
    def clear(self) -> None: ...
    @overload
    def pop(self, key: str, default: None = None) -> _MessageT | None: ...
    @overload
    def pop(self, key: str, default: _T) -> _MessageT | _T: ...
    def popitem(self) -> tuple[str, _MessageT]: ...
    def update(self, arg: _HasIteritems | _HasItems | Iterable[tuple[str, _MessageData]] | None = None) -> None: ...
    @abstractmethod
    def flush(self) -> None: ...
    @abstractmethod
    def lock(self) -> None: ...
    @abstractmethod
    def unlock(self) -> None: ...
    @abstractmethod
    def close(self) -> None: ...
    if sys.version_info >= (3, 9):
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

class Maildir(Mailbox[MaildirMessage]):
    colon: str
    def __init__(
        self, dirname: StrPath, factory: Callable[[IO[Any]], MaildirMessage] | None = None, create: bool = True
    ) -> None: ...
    def add(self, message: _MessageData) -> str: ...
    def remove(self, key: str) -> None: ...
    def __setitem__(self, key: str, message: _MessageData) -> None: ...
    def get_message(self, key: str) -> MaildirMessage: ...
    def get_bytes(self, key: str) -> bytes: ...
    def get_file(self, key: str) -> _ProxyFile[bytes]: ...
    def iterkeys(self) -> Iterator[str]: ...
    def __contains__(self, key: str) -> bool: ...
    def __len__(self) -> int: ...
    def flush(self) -> None: ...
    def lock(self) -> None: ...
    def unlock(self) -> None: ...
    def close(self) -> None: ...
    def list_folders(self) -> list[str]: ...
    def get_folder(self, folder: str) -> Maildir: ...
    def add_folder(self, folder: str) -> Maildir: ...
    def remove_folder(self, folder: str) -> None: ...
    def clean(self) -> None: ...
    def next(self) -> str | None: ...

class _singlefileMailbox(Mailbox[_MessageT], metaclass=ABCMeta):
    def add(self, message: _MessageData) -> str: ...
    def remove(self, key: str) -> None: ...
    def __setitem__(self, key: str, message: _MessageData) -> None: ...
    def iterkeys(self) -> Iterator[str]: ...
    def __contains__(self, key: str) -> bool: ...
    def __len__(self) -> int: ...
    def lock(self) -> None: ...
    def unlock(self) -> None: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...

class _mboxMMDF(_singlefileMailbox[_MessageT]):
    def get_message(self, key: str) -> _MessageT: ...
    def get_file(self, key: str, from_: bool = False) -> _PartialFile[bytes]: ...
    def get_bytes(self, key: str, from_: bool = False) -> bytes: ...
    def get_string(self, key: str, from_: bool = False) -> str: ...

class mbox(_mboxMMDF[mboxMessage]):
    def __init__(self, path: StrPath, factory: Callable[[IO[Any]], mboxMessage] | None = None, create: bool = True) -> None: ...

class MMDF(_mboxMMDF[MMDFMessage]):
    def __init__(self, path: StrPath, factory: Callable[[IO[Any]], MMDFMessage] | None = None, create: bool = True) -> None: ...

class MH(Mailbox[MHMessage]):
    def __init__(self, path: StrPath, factory: Callable[[IO[Any]], MHMessage] | None = None, create: bool = True) -> None: ...
    def add(self, message: _MessageData) -> str: ...
    def remove(self, key: str) -> None: ...
    def __setitem__(self, key: str, message: _MessageData) -> None: ...
    def get_message(self, key: str) -> MHMessage: ...
    def get_bytes(self, key: str) -> bytes: ...
    def get_file(self, key: str) -> _ProxyFile[bytes]: ...
    def iterkeys(self) -> Iterator[str]: ...
    def __contains__(self, key: str) -> bool: ...
    def __len__(self) -> int: ...
    def flush(self) -> None: ...
    def lock(self) -> None: ...
    def unlock(self) -> None: ...
    def close(self) -> None: ...
    def list_folders(self) -> list[str]: ...
    def get_folder(self, folder: StrPath) -> MH: ...
    def add_folder(self, folder: StrPath) -> MH: ...
    def remove_folder(self, folder: StrPath) -> None: ...
    def get_sequences(self) -> dict[str, list[int]]: ...
    def set_sequences(self, sequences: Mapping[str, Sequence[int]]) -> None: ...
    def pack(self) -> None: ...

class Babyl(_singlefileMailbox[BabylMessage]):
    def __init__(self, path: StrPath, factory: Callable[[IO[Any]], BabylMessage] | None = None, create: bool = True) -> None: ...
    def get_message(self, key: str) -> BabylMessage: ...
    def get_bytes(self, key: str) -> bytes: ...
    def get_file(self, key: str) -> IO[bytes]: ...
    def get_labels(self) -> list[str]: ...

class Message(email.message.Message):
    def __init__(self, message: _MessageData | None = None) -> None: ...

class MaildirMessage(Message):
    def get_subdir(self) -> str: ...
    def set_subdir(self, subdir: Literal["new", "cur"]) -> None: ...
    def get_flags(self) -> str: ...
    def set_flags(self, flags: Iterable[str]) -> None: ...
    def add_flag(self, flag: str) -> None: ...
    def remove_flag(self, flag: str) -> None: ...
    def get_date(self) -> int: ...
    def set_date(self, date: float) -> None: ...
    def get_info(self) -> str: ...
    def set_info(self, info: str) -> None: ...

class _mboxMMDFMessage(Message):
    def get_from(self) -> str: ...
    def set_from(self, from_: str, time_: bool | tuple[int, int, int, int, int, int, int, int, int] | None = None) -> None: ...
    def get_flags(self) -> str: ...
    def set_flags(self, flags: Iterable[str]) -> None: ...
    def add_flag(self, flag: str) -> None: ...
    def remove_flag(self, flag: str) -> None: ...

class mboxMessage(_mboxMMDFMessage): ...

class MHMessage(Message):
    def get_sequences(self) -> list[str]: ...
    def set_sequences(self, sequences: Iterable[str]) -> None: ...
    def add_sequence(self, sequence: str) -> None: ...
    def remove_sequence(self, sequence: str) -> None: ...

class BabylMessage(Message):
    def get_labels(self) -> list[str]: ...
    def set_labels(self, labels: Iterable[str]) -> None: ...
    def add_label(self, label: str) -> None: ...
    def remove_label(self, label: str) -> None: ...
    def get_visible(self) -> Message: ...
    def set_visible(self, visible: _MessageData) -> None: ...
    def update_visible(self) -> None: ...

class MMDFMessage(_mboxMMDFMessage): ...

class _ProxyFile(Generic[AnyStr]):
    def __init__(self, f: IO[AnyStr], pos: int | None = None) -> None: ...
    def read(self, size: int | None = None) -> AnyStr: ...
    def read1(self, size: int | None = None) -> AnyStr: ...
    def readline(self, size: int | None = None) -> AnyStr: ...
    def readlines(self, sizehint: int | None = None) -> list[AnyStr]: ...
    def __iter__(self) -> Iterator[AnyStr]: ...
    def tell(self) -> int: ...
    def seek(self, offset: int, whence: int = 0) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None: ...
    def readable(self) -> bool: ...
    def writable(self) -> bool: ...
    def seekable(self) -> bool: ...
    def flush(self) -> None: ...
    @property
    def closed(self) -> bool: ...
    if sys.version_info >= (3, 9):
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

class _PartialFile(_ProxyFile[AnyStr]):
    def __init__(self, f: IO[AnyStr], start: int | None = None, stop: int | None = None) -> None: ...

class Error(Exception): ...
class NoSuchMailboxError(Error): ...
class NotEmptyError(Error): ...
class ExternalClashError(Error): ...
class FormatError(Error): ...
