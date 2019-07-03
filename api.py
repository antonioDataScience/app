from bs4 import BeautifulSoup
import re
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def formaturl(url):
    if not re.match('(?:http|https)://', url):
        return 'https://{}'.format(url)
    return url

@app.route("/",methods=['POST'])
def download():
    if request.method == 'POST':
        ctx = {}
        data = request.json
        url = formaturl(data['url'])
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'lxml')
        image_tags = soup.findAll('img')
        for i,image_tag in enumerate(image_tags):
            ctx[i] = {'url':image_tag.get('src')}
            # print(image_tag.get('src'))
    return jsonify(ctx)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)

