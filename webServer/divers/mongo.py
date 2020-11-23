# coding=UTF-8
from flask import Response,current_app,request,session
from sqlalchemy import text
from webServer.customer import Func,ApiCorsResponse
import json,time,datetime,re




class MongoDb():
    @classmethod
    def get_request_num_by_url(cls):
        if request.args.get('type') == 'init':
            # 　一分钟 * 10 10分钟
            limit = 60 * 10
        else:
            limit = 5

        # session['now_timestamp'] = int(time.time())
        collection = current_app.db_engine_table

        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        total = current_app.db[collection].find({'time_str': {'$regex': '^%s' % today}}).count()

        res = current_app.db[collection].aggregate([
            {'$match': {'time_str': {'$regex': '^%s' % today}}},
            {'$group': {'_id': '$request_url', 'total_num': {'$sum': 1}}},
            {'$project': {
                'ip': '$_id',
                'total_num': 1,
                '_id': 0,
                'percent': {'$toDouble': {'$substr': [{'$multiply': [{'$divide': ['$total_num', total]}, 100]}, 0, 4]}}
            }
            },
            {'$sort': {'total_num': -1}},
            {'$limit': 50}
        ])

        data = list(res)
        data.reverse()

        return ApiCorsResponse.response(data)

    @classmethod
    def get_request_num_by_ip(cls):
        if request.args.get('type') == 'init':
            # 　一分钟 * 10 10分钟
            limit = 60 * 10
        else:
            limit = 5

        session['now_timestamp'] = int(time.time())

        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # total = current_app.db[current_app.db_engine_table].find({'time_str': {'$regex': '^%s' % today}}).count()

        res = current_app.db[current_app.db_engine_table].aggregate([
            {'$match': {'time_str': {'$regex': '^%s' % today}}},
            {'$group': {'_id': '$remote_addr', 'total_num': {'$sum': 1}}},
            {'$project': {
                'remote_addr':'$_id',
                'total_num': 1,
                '_id':0
                # 'percent':{ '$toDouble': {'$substr':[  {'$multiply':[ {'$divide':['$total_num' , total]} ,100] }  ,0,4  ] }   }
            }
            },
            {'$sort': {'total_num': -1}},
            {'$limit': 50}
        ])



        data = list(res)
        data.reverse()
        return ApiCorsResponse.response(data)

    @classmethod
    def get_request_urls_by_ip(cls):
        if not request.args.get('ip'):
            return ApiCorsResponse.response('缺少ip参数', False)

        session['now_timestamp'] = int(time.time())

        collection = current_app.db_engine_table

        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # total = current_app.db[collection].find({'time_str': {'$regex': '^%s' % today}}).count()

        res = current_app.db[collection].aggregate([
            {'$match': {'time_str': {'$regex': '^%s' % today}, 'remote_addr': request.args.get('ip')}},
            {'$group': {'_id': '$request_url', 'total_num': {'$sum': 1}}},
            {'$project': {
                'total_num': 1,
                'request_url': '$_id',
            }
            },
            {'$sort': {'total_num': -1}},
            {'$limit': 20}
        ])


        data = list(res)
        data.reverse()
        return ApiCorsResponse.response(data)

    @classmethod
    def get_request_num_by_status(cls):
        session['now_timestamp'] = int(time.time())

        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # total = current_app.mongo.db.logger.find({'time_str': {'$regex': '^%s' % today}}).count()

        res = current_app.db[current_app.db_engine_table].aggregate([
            {'$match': {'time_str': {'$regex': '^%s' % today}, 'status': {'$ne': '200'}}},
            {'$group': {'_id': '$status', 'total_num': {'$sum': 1}}},
            {'$project': {'status': '$_id', 'total_num': 1, '_id': 0}},
            {'$sort': {'total_num': -1}},
        ])

        data = list(res)
        data.reverse()

        return ApiCorsResponse.response(data)

    @classmethod
    def get_request_num_by_status_code(cls):
        if not request.args.get('code'):
            return ApiCorsResponse.response('缺少code参数', False)

        session['now_timestamp'] = int(time.time())

        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        arg = re.findall('\d+?', request.args.get('code'))
        res = current_app.db[current_app.db_engine_table].aggregate([
            {'$match': {'time_str': {'$regex': '^%s' % today}, 'status': ''.join(arg)}},
            {'$group': {'_id': '$request_url', 'total_num': {'$sum': 1}}},
            {'$project': {'request_url': '$_id', 'total_num': 1, '_id': 0}},
            {'$sort': {'total_num': -1}},
        ])

        data = list(res)
        data.reverse()

        return ApiCorsResponse.response(data)

    @classmethod
    def get_request_num_by_secends(cls):
        if request.args.get('type') == 'init':
            # 　一分钟 * 10 10分钟
            limit = 60 * 10
        else:
            limit = 5

        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        res = current_app.db[current_app.db_engine_table].aggregate([
            {'$match': {'time_str': {'$regex': '^%s' % today}}},
            {'$group': {'_id': '$timestamp', 'total_num': {'$sum': 1}}},
            {'$project': {'timestamp': '$_id', 'total_request_num': '$total_num', '_id': 0}},
            {'$sort': {'timestamp': -1}},
            {'$limit': limit}
        ])

        data = []
        for i in res:
            item = {}
            # item['timestamp'] = time.strftime('%H:%M:%S', time.localtime(i['timestamp']))
            # * 1000 for js timestamp
            item['timestamp'] = i['timestamp'] * 1000
            item['total_request_num'] = i['total_request_num']
            data.append(item)

        data.reverse()
        return ApiCorsResponse.response(data)

    @classmethod
    def get_request_num_by_province(cls):
        session['now_timestamp'] = int(time.time())

        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))


        # total = current_app.mongo.db.logger.find({'time_str': {'$regex': '^%s' % today}}).count()

        res = current_app.db[current_app.db_engine_table].aggregate([
            {'$match': {'time_str': {'$regex': '^%s' % today}}},
            {'$group': {'_id': '$province', 'total_num': {'$sum': 1}}},
            {'$project': {'province': '$_id', 'value': '$total_num', '_id': 0}},
            {'$sort': {'total_num': -1}},
        ])

        data = list(res)
        data.reverse()

        return ApiCorsResponse.response(data)

