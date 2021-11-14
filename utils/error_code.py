from django.db.models import IntegerChoices


class ErrorCode(IntegerChoices):
    # 100-199 error
    # 200-299 green
    # 300-399 warning
    # 400-499 info
    SUCCEED = 200
    FAILED = 100

    FORBIDDEN = 150
    NOTFOUND = 151
    # login
    DATABASE_ERROR = 101
    USERNOTFOUND = 102
    AUTHENTICATION_FAILED = 103
    BLOCKED = 104
    FORMATERROR = 105
    RELOGIN = 106
    NOTLOGIN = 107
    ROBOT_BEHAVIOR = 108
    NETWORK = 109

    USERNAMEREPEAT = 110
    EMAILREPEAT = 111

    EMAILSENDERROR = 112

    CHANGEORG = 113

    CANTDISCUSS = 115

    SCRIPT=116

    RUNNING = 401

    SCRIPTBLOCKED = 301

    # TOO_MANY_TIMES = 106
    # ACCESS_DENIED = 105
    # NOT_LOGIN = 106
    # ROBOT_BEHAVIOR = 107
    #
    #
    # ILLEGAL_ACCESS = 200
    # DATA_FALSIFIED = 201