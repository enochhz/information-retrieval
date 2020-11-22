import redis
import pandas as pd

PAGE_LIMIT = 10000

class id_mapper():
    redis_db = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)
    all_keys = redis_db.scan_iter()
    url_id = {}
    id = 0
    count = 0
    id_map = {}

    # def __init__():
    #     print(self.redis_db)
        
    def generate_id(self):
        for key in self.all_keys:
            # print(f'{key}: {redis_db.get(key)}')
            if not key in self.url_id.keys():
                self.url_id[key] = self.id
                self.id += 1;
            self.count += 1
            outlink_list = self.redis_db.get(key).split(',')
            for url in outlink_list:
                if not url in self.url_id.keys():
                    self.url_id[url] = self.id
                    self.id += 1
                self.count += 1
            # break
            if self.id > PAGE_LIMIT:
                break

        # print()
        # print(url_id)

        url_id_df = pd.DataFrame(columns = ['url', 'id'])
        for _url, _id in self.url_id.items():
            url_id_df = url_id_df.append({  # set the url and id to df
                    'url': _url,
                    'id': _id,
                }, ignore_index=True)

        url_id_df.to_csv('url_id.csv')

        print('id', self.id)
        print('count', self.count)

    def id_mapping(self):
        for key in self.all_keys: 
            # print('key: ', key)
            if not key in self.url_id.keys():
                continue
            id_key = self.url_id[key]
            if id_key > PAGE_LIMIT:
                break
            if not id_key in self.id_map:
                self.id_map[id_key] = []
            outlink_list = self.redis_db.get(key).split(',')

            for outlink in outlink_list:
                if outlink in self.url_id.keys():
                    # print('outlinks: ', outlink)
                    self.id_map[id_key].append(self.url_id[outlink])
            
            # if len(self.id_map) >= 100:
            for _key, _outlinks in self.id_map.items():
                print(_key, _outlinks);

                id_map_df = pd.DataFrame(columns = ['seed', 'outlinks'])
                
                id_map_df = id_map_df.append({  # set the url and id to df
                    'seed': _key,
                    'outlinks': _outlinks,
                }, ignore_index=True)

                id_map_df.to_csv('outlink_maps/' + str(_key) + '.csv')
            # self.id_map.clear()
            # if len(self.id_map) > 10:
            #     break
        
        
            # id_map_df.to_csv('id_map.csv')

mapper = id_mapper()
mapper.generate_id()
mapper.id_mapping()
