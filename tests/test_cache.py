from cache import Cache


def test_set_key():
    cache = Cache(1, 3600)
    cache['test'] = 'ok'
    assert 'ok' == cache.get('test')
    assert 1 == len(cache)


def test_evicts_least_recently_used_keys():
    cache = Cache(1, 3600)

    for i in range(5):
        cache['test'] = i

    assert 4 == cache.get('test')
    assert 1 == len(cache)


def test_expires_keys():
    cache = Cache(1, -1)
    cache['test'] = 'ok'
    assert None is cache.get('test')
    assert 0 == len(cache)
    assert None is cache.head
    assert None is cache.tail


def test_evicts_node_in_between():
    cache = Cache(3, 3600)

    cache[0] = 'cat'
    cache[1] = 'cat'
    cache[2] = 'cat'

    cache.get(0)
    cache.get(2)

    cache[4] = 'dog'

    assert None is cache.get(1)


def test_evicts_all_prev_nodes():
    cache = Cache(3, 3600)

    cache[0] = 'cat'
    cache[1] = 'cat'
    cache[2] = 'cat'

    cache[4] = 'cat'
    cache[5] = 'cat'
    cache[6] = 'cat'

    assert [None] * 3 == [cache.get(0), cache.get(1), cache.get(2)]


def test_update_bumps_the_key():
    cache = Cache(2, 3600)

    cache[1] = 'cat'
    cache[2] = 'cat'

    cache[1] = 'cat'
    cache[3] = 'cat'

    assert None is cache.get(2)
