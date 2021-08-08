import json
import pytest
import config
import bcrypt

from sqlalchemy import create_engine, text
from app import create_app

database = create_engine(config.test_config['DB_URL'], encoding='utf-8', max_overflow=0)

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TEST'] = True
    api = app.test_client()

    return api

def setup_function():
    # Create a test user
    hashed_password = bcrypt.hashpw(b"test password", bcrypt.gensalt())
    new_users = [{
        'id': 1,
        'name': '오지환',
        'email': 'asdf@naver.com',
        'profile': 'male',
        'hashed_password': hashed_password
    }, {
        'id': 2,
        'name': '홍길동',
        'email': 'hong@naver.com',
        'profile': 'male',
        'hashed_password': hashed_password
    }]
    database.execute(text("""
        INSERT INTO users (id, name, email, profile, hashed_password)
        VALUE (:id, :name, :email, :profile, :hashed_password)
    """), new_users)

    database.execute(text("""
        INSERT INTO tweets (user_id, tweet)
        VALUE (2, "Hello I'm Hong")
    """))

def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))

def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data

def test_login(api):
    resp = api.post('/login', data=json.dumps({
        'email': 'asdf@naver.com',
        'password': 'test password'
    }), content_type='application/json')

    assert b"access_token" in resp.data

def test_tweet(api):

    # login test
    resp = api.post('/login', data=json.dumps({'email': 'asdf@naver.com', 'password': 'test password'}), content_type='application/json')
    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    # tweet test
    resp = api.post('/tweet',
                    data=json.dumps({'tweet': 'I am test tweet!'}),
                    content_type='application/json',
                    headers={'Authorization': access_token}
                    )
    assert resp.status_code == 200

    # check tweet
    resp = api.get('/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': [
            {
                'user_id': 1,
                'tweet': "I am test tweet!"
            }
        ]
    }

def test_unauthorized(api):
    resp = api.post('/tweet', data=json.dumps({
        'tweet': 'Hello world'
    }), content_type='application/json')

    assert resp.status_code == 401

    resp = api.post('/follow', data=json.dumps({
        'follow': 2
    }), content_type='application/json')

    assert resp.status_code == 401

    resp = api.post('/unfollow', data=json.dumps({
        'unfollow': 2
    }), content_type='application/json')

    assert resp.status_code == 401

def test_follow(api):
    # Login
    resp = api.post('/login', data=json.dumps({
        'email': 'asdf@naver.com',
        'password': 'test password'
    }), content_type='application/json')

    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp = api.post('/follow', data=json.dumps({
        'follow': 2
    }), content_type='application/json', headers={'Authorization': access_token})

    assert resp.status_code == 200

    resp = api.get('timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert tweets == {
        'user_id': 1,
        'timeline': [{
            'user_id': 2,
            'tweet': "Hello I'm Hong"
        }]
    }

def test_unfollow(api):
    resp = api.post('/login', data=json.dumps({
        'email': 'asdf@naver.com',
        'password': 'test password'
    }), content_type='application/json')

    resp_json = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp = api.post('/follow', data=json.dumps({
        'follow': 2
    }), content_type='application/json', headers={'Authorization': access_token})

    assert resp.status_code == 200

    resp = api.get('timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': [{
            'user_id': 2,
            'tweet': "Hello I'm Hong"
        }]
    }

    resp = api.post('/unfollow', data=json.dumps({'unfollow': 2}), content_type='application/json', headers={'Authorization': access_token})

    assert resp.status_code == 200

    resp = api.get('/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == 200
    assert tweets == {
        'user_id': 1,
        'timeline': []
    }