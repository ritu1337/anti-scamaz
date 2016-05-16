#anti-scamaz
Anti-scamaz is a Chrome extension that analyzes every imgur image.

It displays:

1. Real image format: (JPG, PNG, GIF...)
2. Animated: Yes/No
3. Duration in seconds (if it's animated) to know when it loops, so that you don't get tricked into showing a dick on stream.
4. WutFace Alert about scamaz images (JPG, PNG...) that really are animated gifs.

It looks like this:

![](http://i.imgur.com/1Zrfp2T.png)

#### Short Video Demonstration (stream safe ❤)
####https://www.youtube.com/watch?v=E57P2snKWZk

#### Links from the video
Safe for stream, but you can preview them here.

1. http://i.imgur.com/lwaKDvG.png  - PNG direct link
2. http://i.imgur.com/Mso98Dt.gifv - GIF direct link
3. http://imgur.com/3nxPTwW        - GIF on imgur page
4. http://i.imgur.com/ZbTIpKU.jpg  - fake animated JPG (scamaz)

#### Author
![RiTu1337](http://i.imgur.com/COQkzio.png)

#### Contributors
![saevae](http://i.imgur.com/X2IZoCT.png) (CSS)

#### Install:
Chrome extension: https://chrome.google.com/webstore/detail/anti-scamaz/finbfifiddoeknaddinifpjofifcicof

#### Protip:
To make sure that the image status is not photoshopped in, it's a good idea to hover your mouse pointer over it, to see if it's a real text:

![](http://i.imgur.com/DXhSHGr.png)

#### How it works
As soon as you open an imgur link, the anti-scamaz chrome extension sends the imgur link to the server. The server application opens and analyzes every frame (regardless of the image format) and sends the results back to chrome. It detects animated images 100% of the time.

#### Privacy
- Request to the API server is sent over a secure https connection.
- The only information being sent is the imgur link.
- Use proxy in Chrome if you don't want the server to see your IP.
- IP logging is completely disabled.
