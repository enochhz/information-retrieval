import redis
import pandas as pd

# PAGE_LIMIT = 150000

class id_mapper():
    redis_db = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)
    all_keys = list(redis_db.scan_iter())
    url_id = {}
    id = 0
    count = 0
    id_map = {}
    outlink_inlink = {}
    visited_order = pd.read_csv ('visited_pages.csv', usecols= ['pages'])
        
    def generate_id(self):
        for i in range(len(self.visited_order)):
            self.url_id[self.visited_order.loc[i, 'pages']] = self.id
            self.id += 1

        url_id_df = pd.DataFrame(columns = ['url', 'id'])
        for _url, _id in self.url_id.items():
            url_id_df = url_id_df.append({  # set the url and id to df
                    'url': _url,
                    'id': _id,
                }, ignore_index=True)

        url_id_df.to_csv('url_id.csv')


    def id_mapping(self):
        for i in range(len(self.visited_order)):
            key = self.visited_order.loc[i, 'pages']

            if key in self.all_keys and key in self.url_id:
                # print("key: ", key)
                id_key = self.url_id[key]
                self.id_map[id_key] = []

                outlink_list = self.redis_db.get(key).split(',')
                for outlink in outlink_list:
                    if outlink in self.url_id.keys():
                        self.id_map[id_key].append(self.url_id[outlink])

                        if not self.url_id[outlink] in self.outlink_inlink:
                            self.outlink_inlink[self.url_id[outlink]] = 1
                        else:
                            self.outlink_inlink[self.url_id[outlink]] += 1

        for _key, _outlinks in self.id_map.items():
            id_map_df = pd.DataFrame(columns = ['seed', 'outlinks'])
            id_map_df = id_map_df.append({  # set the url and id to df
                'seed': _key,
                'outlinks': _outlinks,
            }, ignore_index=True)
            id_map_df.to_csv('outlink_maps/' + str(_key) + '.csv')

        print(self.outlink_inlink)
        print(len(self.outlink_inlink))

mapper = id_mapper()
mapper.generate_id()
mapper.id_mapping()
