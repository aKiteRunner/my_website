# For all constants and environment variables
from enum import IntEnum
PAGE_MAX = 12


class Authority(IntEnum):
    USER = 1
    ADMINISTRATOR = 2
    SUPER_ADMINISTRATOR = 3


class QuestionAuthority(IntEnum):
    All = 1
    CATEGORY = 2
    OWNER = 3
