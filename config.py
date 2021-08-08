db = {
    'user' : 'root',
    'password': 'asdqwe6512',
    'host': 'python-backend-test.cz2kokgttp4v.ap-northeast-2.rds.amazonaws.com',
    'port': '3306',
    'database': 'miniter'
}
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY = 'some_super_secret_key'

test_db = {
    'user': 'root',
    'password': 'asdqwe1',
    'host': 'localhost',
    'port': 3306,
    'database': 'test_db'
}

test_config = {
    'DB_URL': f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
    'JWT_SECRET_KEY': 'test_secret_key'
}
