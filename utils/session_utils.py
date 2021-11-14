from typing import Dict

import aioredis
from asgiref.sync import sync_to_async, async_to_sync
from django.http.request import *
from django.contrib.sessions.backends.cache import SessionStore
# from Store import config
from utils.error_code import ErrorCode
from utils.status import *

hash_pool = None


@async_to_sync
async def init():
    global hash_pool
    hash_pool = await aioredis.create_redis_pool(**config.django_hash_session_db)


init()


async def set_user_info(user_info: Dict, request: HttpRequest) -> int:
    """
    :param user_info:
    :param request:
    :return:
    """
    try:
        request.session['is_login'] = UserStatus.HALF
        request.session['active'] = user_info['active']
        request.session['id'] = user_info['id']
        request.session['email'] = user_info['email']
        request.session['gender'] = user_info['gender']
        request.session['rating'] = user_info['rating']
        request.session['statistic_info'] = user_info['statistic_info']
        request.session['accept_problem'] = set(user_info['accept_problem'] if user_info['accept_problem'] else [])
        request.session['attempt_problem'] = set(user_info['attempt_problem'] if user_info['attempt_problem'] else [])
        request.session['motto'] = user_info['motto'] if user_info['motto'] else ''
        request.session['avatar'] = user_info['avatar']
        request.session['username'] = user_info['username']
        request.session['is_admin'] = user_info['is_admin']
        request.session['can_discuss'] = user_info['can_discuss']
        request.session['organizations'] = user_info['organizations']
        request.session['courses'] = user_info['courses']
        request.session['team'] = user_info['team']
        request.session['group'] = user_info['group']
        request.session['active_organization'] = {'id': -1, 'name': '', 'nickname': ''}
        request.session['voted'] = user_info['voted']
        old_session = await hash_pool.get(user_info['id'])
        if old_session:
            await delete_key(session_key=old_session)
        await hash_pool.set(user_info['id'], request.session.session_key)
        return ErrorCode.SUCCEED
    except Exception as e:
        # TODO log
        print(e)
        return ErrorCode.DATABASE_ERROR


@sync_to_async
def cycle_key(request: HttpRequest) -> None:
    request.session.cycle_key()

@sync_to_async
def delete_key(session_key: str) -> None:
    s = SessionStore(session_key=session_key)
    s.delete()