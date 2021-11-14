import ast
import re
from typing import Any
from typing import Tuple, List

import aiohttp
from django.http.response import *

# from Store.config import *
from utils.session_utils import *
from utils.status import UserStatus


class Resp(dict):
    def __init__(self, status=ErrorCode.FAILED, **kwargs):
        super(Resp, self).__init__(status=status, **kwargs)


def check_password(password: str) -> bool:
    if not password or type(password) != str or not re.match("^[0-9a-zA-Z]{6,16}$", password):
        return False
    return True


def check_username(username: str) -> bool:
    if not username or type(username) != str or not re.match("^[0-9a-zA-Z]{5,30}$", username):
        return False
    return True


def check_email(email: str) -> bool:
    if not email or type(email) != str or not re.match("[^@]+@[^@]+\.[^@]+", email):
        return False
    return True


async def is_login(request: HttpRequest) -> int:
    """
    :param request:
    :return:
    """
    return request.session.get('is_login', UserStatus.NOTLOGIN)


# async def get_recaptcha_score(code: str) -> float:
#     """
#     :param code:
#     :return:
#     """
#     async with aiohttp.request(method='POST', url='https://www.recaptcha.net/recaptcha/api/siteverify', data=dict(
#             secret=reCaptchaV3_secretkey,
#             response=code
#     )) as resp:
#         if resp.status != 200:
#             return -1
#         response = await resp.json()
#         if not response.get('success', False):
#             return -1
#         return response.get('score', 0)


# async def get_github_access_token(code: str) -> str:
#     """
#     :param code:
#     :return:
#     """
#     async with aiohttp.request(method='POST', url='https://github.com/login/oauth/access_token', data=dict(
#             client_id=github_oauth_client_id,
#             client_secret=github_oauth_client_secret,
#             code=code
#     ), headers=dict(Accept='application/json')) as resp:
#         if resp.status == 200:
#             response = await resp.json()
#             return response.get('access_token', None)
#         else:
#             return None


async def get_github_userinfo(token: str) -> Dict[str, Any]:
    """
    :param token:
    :return:
    """
    try:
        async with aiohttp.request(method='GET', url=f'https://api.github.com/user?access_token={token}', headers=dict(
                Accept='application/json',
                Authorization=f'token {token}'
        )) as resp:
            if resp.status == 200:
                response = await resp.json()
                return response.get('id', None)
            else:
                return None
    except Exception as e:
        print(e)
        return None


async def login_user(request: HttpRequest, userinfo: Dict) -> Resp:
    """
    :param request:
    :param userinfo:
    :return:
    """
    await cycle_key(request)
    code = await set_user_info(userinfo, request)
    return Resp(
        status=code,
        userInfo=dict(
            username=userinfo['username'],
            rating=userinfo['rating'],
            avatar=userinfo['avatar'],
            outerRole='default' if not userinfo['is_admin'] else 'webmaster'
        ),
        organizations=[
            userinfo['organizations'][i]
            for i in userinfo['organizations']
        ]
    )


def get_ip(request: HttpRequest) -> str:
    real_ip = request.META.get('HTTP_X_REAL_IP', None)
    if not real_ip:
        real_ip = request.META.get('HTTP_REMOTE_USER_IP', None)
        if not real_ip:
            real_ip = request.META.get("REMOTE_ADDR", '127.0.0.1')
    print(f"Get IP: {real_ip}")
    return real_ip


def get_user_key(request: HttpRequest) -> int:
    print(f"Get User Id: {request.session.get('id', None)}")
    if request.session.get('is_login', UserStatus.NOTLOGIN) == UserStatus.NOTLOGIN:
        return None
    else:
        return request.session.get('id', None)


async def find_course(request: HttpRequest, course_id: str) -> Dict[str, Any] or None:
    for i in request.session.get('courses', []):
        if i['course_id'] == course_id:
            return i
    return None


async def get_item_range(page: str, offset: str) -> Tuple[bool, int, int]:
    try:
        page = int(page)
        offset = int(offset)
        if page <= 0 or offset not in range(1, 51):
            return False, 0, 0
        return True, (page - 1) * offset, page * offset
    except Exception:
        return False, 0, 0


async def get_problem_name_and_tags(name: str, tags: str) -> Tuple[bool, str, List[str]]:
    try:
        if len(name) > 64 or len(tags) > 128:
            return False, '', []
        name = name.strip()
        tags = ast.literal_eval(tags)
        if len(tags) > 5:
            return False, '', []
        return True, name, tags
    except Exception:
        return False, '', []


async def check_course_admin(request, course_id, requirements: set):
    if request.session.get('is_admin', False):
        return True
    course = request.session.get('courses', dict()).get(course_id, dict())
    if not course.get('is_admin', False):
        return False
    au_have = set(
        course.get('authority', [])
    )
    if len(requirements - au_have) == 0:
        return True
    return False

def sync_check_course_admin(request, course_id, requirements: set):
    if request.session.get('is_admin', False):
        return True
    course = request.session.get('courses', dict()).get(course_id, dict())
    if not course.get('is_admin', False):
        return False
    au_have = set(
        course.get('authority', [])
    )
    if len(requirements - au_have) == 0:
        return True
    return False


async def get_group_id_in(request, course_id):
    course = request.session.get('courses', dict()).get(course_id, dict())
    group = course.get('group', None)
    return None if group is None else group.get('group_id', None)


async def get_group_name_in(request, course_id):
    course = request.session.get('courses', dict()).get(course_id, dict())
    group = course.get('group', None)
    return None if group is None else group.get('name', None)


def get_homework_status(start, alert, end):
    now = timezone.now()
    if now >= end:
        return 4
    elif now < start:
        return 3
    elif now < alert:
        return 2
    return 1