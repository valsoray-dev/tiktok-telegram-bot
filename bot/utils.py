import logging
from collections import UserDict
from typing import Any, TypeVar

import pydantic
from pydantic_core import CoreSchema, core_schema
from typing_extensions import override

logger = logging.getLogger(__name__)


T = TypeVar("T")


def split_list_into_chunks(arr: list[T], chunk_size: int) -> list[list[T]]:
    return [arr[i : i + chunk_size] for i in range(0, len(arr), chunk_size)]


class HeaderMap(UserDict[str, str]):
    """Case-insensitive mapping for HTTP header fields.

    Every key is normalised with ``str.lower()`` on insert, lookup,
    membership tests and deletion, so the following spellings all
    address the same entry: ``"Content-Type"``, ``"content-type"``,
    ``"CONTENT-TYPE"`` etc.

    Only the lower-case form is kept internally; the original
    capitalisation is not preserved.

    Example:
    -------
        >>> h = HeaderMap()
        >>> h["Content-Type"] = "application/json"
        >>> h["content-type"]
        'application/json'
        >>> "CONTENT-TYPE" in h
        True
        >>> h
        {'content-type': 'application/json'}

    """

    @override
    def __getitem__(self, key: str) -> str:
        return self.data[key.lower()]

    @override
    def __setitem__(self, key: str, value: str) -> None:
        self.data[key.lower()] = value

    @override
    def __delitem__(self, key: str) -> None:
        del self.data[key.lower()]

    @override
    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key.lower() in self.data

    @classmethod
    def __get_pydantic_core_schema__(  # noqa: PLW3201
        cls,
        source_type: Any,  # noqa: ANN401
        handler: pydantic.GetCoreSchemaHandler,
    ) -> CoreSchema:
        dict_schema = core_schema.dict_schema(
            keys_schema=core_schema.str_schema(),
            values_schema=core_schema.str_schema(),
        )

        # Whatever that shit is doing
        return core_schema.no_info_after_validator_function(cls, dict_schema)
