import time

from etcd3gw.client import Etcd3Client
from etcd3gw.lock import Lock


def main():
    client = Etcd3Client()
    lock = Lock('foo-%s' % time.time(), ttl=30, client=client)

    print('Acquire: %s' % lock.acquire())

    print('Acquired: %s' % lock.is_acquired())
    print('Refresh quickly: %s' % lock.refresh())
    time.sleep(60)

    # This will return this stack trace as the lease has expired...
    #
    # Traceback (most recent call last):
    #   File "ttl.py", line 18, in <module>
    #     main()
    #   File "ttl.py", line 14, in main
    #     print('Refresh slowly: %s' % lock.refresh())
    #   File "/usr/local/lib/python3.8/dist-packages/etcd3gw/lock.py", line 101, in refresh
    #     return self.lease.refresh()
    #   File "/usr/local/lib/python3.8/dist-packages/etcd3gw/lease.py", line 64, in refresh
    #     return int(result['result']['TTL'])
    # KeyError: 'TTL'

    print('Acquired: %s' % lock.is_acquired())
    print('Refresh slowly: %s' % lock.refresh())


if __name__ == '__main__':
    main()
