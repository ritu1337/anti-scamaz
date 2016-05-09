from flask import Flask, request, jsonify, redirect
from logging.handlers import RotatingFileHandler
from cStringIO import StringIO
from lxml.html import fromstring
from PIL import Image
import ujson as json
import requests
import logging
import redis
import re


application = Flask(__name__)
application.config['PROPAGATE_EXCEPTIONS'] = True
# application.debug = True

LOG_FILENAME = '/var/log/imgur/error.log'

formatter = logging.Formatter(
    "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")

handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

application.logger.setLevel(logging.DEBUG)
application.logger.addHandler(handler)

rd = redis.StrictRedis(host='localhost', port=6379, db=0)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8'
}

static_extensions = ['.jpg', '.jpeg', '.png', '.apng', '.bmp']
animated_extensions = ['.gif', '.webm', '.mp4']  # .gifv is covered by .gif


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


def scamaz(is_animated, imgur_url):
    has_static = any([ext in imgur_url for ext in static_extensions])
    has_animated = any([ext in imgur_url for ext in animated_extensions])

    if (
        is_animated and
        'i.imgur.com' in imgur_url and
        (not has_animated or (has_animated and has_static))
    ):
        # is animated but has and no .gif in url, or is like .gif.jpg
        return True
    else:
        return False


def format_url(imgur_url):
    imgur_url = imgur_url.replace('https://', 'http://').replace(
        '.gifv', '.gif').replace('.webm', '.gif').replace('.mp4', '.gif')
    imgur_url = imgur_url.split('?')[0]

    m = re.search(
        r'imgur\.com/(?:\S{1,15}/)?(\w{5,8})\.*?(?:jpg|png|gif|gifv|jpeg|apng|bmp|webm|mp4|/)?', imgur_url)
    imgur_id = m.group(1)
    return imgur_url, imgur_id


@application.route("/", methods=['GET'])
def main():
    return redirect("https://github.com/RiTu1337/anti-scamaz/", code=302)


@application.route('/check', methods=['GET'])
def check():
    try:
        imgur_url = request.args.get('imgur_url')
        application.logger.info(imgur_url)

        if not imgur_url:
            return jsonify(status='bad')

        try:
            imgur_url, imgur_id = format_url(imgur_url)
        except:
            application.logger.error(
                'imgur_url: {}'.format(imgur_url), exc_info=True)
            return jsonify(status='bad')

        try:
            if '/gallery/' in imgur_url.lower() or '/a/' in imgur_url.lower():
                r_gallery = requests.get(imgur_url, headers=headers)
                tree = fromstring(r_gallery.content)
                
                imgur_script = tree.xpath("(//body/div[@id='inside']//div[@class='post-image'])[1]//script")
                m = re.search("gifUrl:(.*)'", imgur_script[0].text)
                
                imgur_url = m.group(1).strip().replace("'//", "http://")
                imgur_url, imgur_id = format_url(imgur_url)
        except:
            try:
                t = tree.xpath("(//body/div[@id='inside']//div[@class='post-image'])[1]//img")
                imgur_url = t[0].get('src').strip().replace("//", "http://")
                imgur_url, imgur_id = format_url(imgur_url)
            except:
                application.logger.error(
                    'imgur_url: {}'.format(imgur_url), exc_info=True)
                return jsonify(status='bad')

        json_str = rd.get(imgur_id)

        if json_str:
            application.logger.info('cached: {}'.format(imgur_id))
            json_obj = json.loads(json_str)
            json_obj['is_scamaz'] = scamaz(json_obj['is_animated'], imgur_url)
            # json_obj['cached'] = True
            return jsonify(**json_obj)

        if 'i.imgur.com' in imgur_url:
            direct = imgur_url
        else:
            # DL non direct links as .gif because we don't know the extension
            direct = 'http://i.imgur.com/{}.gif'.format(imgur_id)

        r = requests.get(direct, headers=headers)

        if not r.ok:
            application.logger.error('imgur_url: {}\ndirect: {}'
                                     .format(imgur_url, direct))
            return jsonify(status='bad')

        try:
            im = Image.open(StringIO(r.content))
        except IOError:
            application.logger.error('imgur_url: {}\nimgur_id: {}\ndirect: {}'
                                     .format(imgur_url, imgur_id, direct), exc_info=True)
            return jsonify(status='bad')

        try:
            im.seek(1)
        except EOFError:
            is_animated = False
        else:
            is_animated = True

        image_format = im.format.replace('JPEG', 'JPG')

        durations = []
        duration_warning = None
        
        if is_animated:
            for frame in iter_frames(im):
                try:
                    durations.append(frame.info['duration'])
                except KeyError:
                    application.logger.info('duration KeyError: {}', imgur_url)
                    duration_warning = "One or more frames have an unknown duration. GIF could be longer!"
                    # pass

            try:
                duration = float("{:.2f}".format(sum(durations) / 1000.0))
                if duration <= 0:
                    duration = "N/A"
                    duration_warning = "Can't find the real GIF duration!"
            except:
                duration = "N/A"
                duration_warning = "Can't find the real GIF duration!"
        else:
            duration = None

        duration_string = str(duration).rstrip('0').rstrip('.')

        is_scamaz = scamaz(is_animated, imgur_url)

        json_obj = {
            'imgur_id': imgur_id,
            'format': image_format,
            'is_animated': is_animated,
            'duration': duration_string,
            'is_scamaz': is_scamaz,
            'duration_warning': duration_warning,
            'status': 'ok'
        }

        # Cache for 1 day
        rd.setex(imgur_id, 86400, json.dumps(json_obj))

        return jsonify(**json_obj)
    except:
        application.logger.error(
            'imgur_url: {}'.format(imgur_url), exc_info=True)
        return jsonify(**json_obj)

if __name__ == "__main__":
    # application.debug = True
    application.run(host='0.0.0.0')
