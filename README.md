# A web crawler prototype
A simple web crawler prototype built with tornado and redis.

## Design decisions
* Failed requests lead to skipped pages. Reason: simplicity for prototyping.
* Instead of checking whether there is an url being fetched that could generate
new urls, storage is simply waiting for 0.5s if the queue is empty.
Reason: simplicity for prototyping.

Steps to run the crawler:
1. Run redis: `redis-server redis.conf`
2. Run app: `python crawler/crawler.py --url http://tomblomfield.com`

## Scalability
If run with `gunicorn`, the number of processes should be ~ 2 times the number
of cores. The optimal number of workers per process needs to be benchmarked.

To scale the storage either randomised sharding is to be implemented
(for redis cluster), or a different kind of distributed storage is to be used.

## Not implemented

* Tests.
* Multiprocessing.
* Benchmarking for optimal number of coroutines per process.
