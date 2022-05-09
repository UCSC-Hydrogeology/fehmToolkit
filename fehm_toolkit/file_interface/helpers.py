import itertools


def grouper(iterable, chunksize):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, chunksize))
        if not chunk:
            return
        yield chunk
