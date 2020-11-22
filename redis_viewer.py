import redis
redis_db = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)
all_keys = redis_db.scan_iter()
count = 0
for key in all_keys: 
    if count == 10: break
    print(f'{key}: {redis_db.get(key)}')
    count += 1