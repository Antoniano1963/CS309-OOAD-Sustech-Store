import uvicorn
import os
import celery
# celery -A Try2 worker -l info -P eventlet
# celery -A Final_Project1 worker -l info -P gevent
# celery -A Final_Project1 beat -l info
# netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
# netsh interface portproxy show all
# wsl -- ifconfig eth0
# netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.25.112.97
# netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=localhost
# python3 manage.py collectstatic
# python3 manage.py rebuild_index
# /usr/local/lib/python3.8/dist-packages/haystack/backends
# cp ChineseAnalyzer.py /usr/local/lib/python3.8/dist-packages/haystack/backends
# cp whoosh_cn_backend.py /usr/local/lib/python3.8/dist-packages/haystack/backends
# ALTER USER postgres WITH PASSWORD '123321';
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Final_Project1.settings')
    uvicorn.run(
        'Final_Project1.asgi:application',
        host='0.0.0.0',
        port=8080,
        log_level='debug',
        reload=False,
        )

if __name__ == "__main__":
    main()
