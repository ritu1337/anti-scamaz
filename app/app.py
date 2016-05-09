from flask import Flask, request, jsonify
from PIL import Image
import requests
import re
from cStringIO import StringIO

application = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8'
}

static_extensions = ['.jpg', '.jpeg', '.png', '.apng', '.bmp']


def iter_frames(im):
    try:
        i = 0
        while 1:
            im.seek(i)
            frame = im.copy()
            yield frame
            i += 1
    except (EOFError, Exception):
        pass


@application.route("/")
def main():
    return "Welcome!"


@application.route('/check', methods=['GET'])
def check():
    try:
        imgur_url = request.args.get('imgur_url')
        print imgur_url

        if not imgur_url:
            return jsonify(status='bad')

        imgur_url = imgur_url.replace('https://', 'http://')

        m = re.search(
            r'imgur\.com/(?:\S{1,15}/)?(\w{6,8})\.*?(?:jpg|png|gif|gifv|jpeg|apng|bmp|webm|mp4|/)?', imgur_url)

        try:
            imgur_id = m.group(1)
        except:
            return jsonify(status='bad')

        if 'i.imgur.com' in imgur_url:
            direct = imgur_url
        else:
            direct = 'http://i.imgur.com/{}.jpg'.format(imgur_id)

        r = requests.get(direct, headers=headers)

        if not r.ok:
            return jsonify(status='bad')

        im = Image.open(StringIO(r.content))

        try:
            im.seek(1)
        except EOFError:
            is_animated = False
        else:
            is_animated = True

        image_format = im.format.replace('JPEG', 'JPG')

        durations = []

        for frame in iter_frames(im):
            try:
                durations.append(frame.info['duration'])
            except KeyError:
                pass

        try:
            duration = float("{:.2f}".format(sum(durations) / 60))
        except:
            duration = 'N/A'

        duration_string = str(duration).rstrip('0').rstrip('.')

        if is_animated and any([ext in imgur_url for ext in static_extensions]):
            # animated and .jpg url
            scamaz = True
        else:
            scamaz = False

        return jsonify(imgur_id=imgur_id,
                       format=image_format,
                       is_animated=is_animated,
                       duration=duration_string,
                       scamaz=scamaz,
                       status='ok')
    except Exception as e:
        print e
        return jsonify(status='bad')

if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0')
