from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import datetime

import schedule

client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://test:test@아이피주소', 27017)
db = client.dbmyproject

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/latest')
def latest():
    return render_template("latest.html")


@app.route('/api/latest', methods=['GET'])
def show_latest_news():
    news = list(db.latestNews.find({}, {'_id': False}).sort('datetime', -1).limit(50))
    return jsonify({'result': 'success', 'all_news': news})


@app.route('/hottest')
def hottest():
    return render_template("hottest.html")


@app.route('/api/hottest', methods=['GET'])
def show_hottest_news():
    date_receive = request.args.get('date')
    print(date_receive)

    date_object = datetime.datetime.strptime(date_receive, '%Y-%m-%d')
    print(date_object)

    news = list(db.hottestNews.find({'save_datetime': date_object}, {'_id': False}).sort('datetime', -1))

    return jsonify({'result': 'success', 'all_news': news})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
