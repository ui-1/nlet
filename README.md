# nlet

Short (n letters, get it? (realistically four lol)) Github usernames so you can impress all the ladies

## Why?

I wanted a cool (short) username for everyone to see how cool i am

## How?

Other such scripts that I've seen tend to check the availability of a username either by checking whether or not the
respective profile page is a 404 or by using the API (ew xd). This has a few issues:
* certain usernames are reserved or something - the profile page is a 404 (no account with that username exists) but you still can't register them. Thus you get a bunch of false positives such as `sex`, `ss` and `api` and even some completely nonsensical ones that are just random characters 
* the api limits the amount of requests per hour. sure, you can generate throwaway accounts automatically (easiest captcha in the world) and use those to rotate tokens but that's annoying and maybe even a bit rude)
* it's kinda sorta quite slow

What we do here instead is emulating that part of the registration process where it asks you to enter a username:
* no captchas, no tokens
* no false positives
* implemented asynchronously and with a task queue, making it quite fast
  * like "400 usernames per second on my oftentimes unusably slow connection" fast
* blocked? just switch proxies))

## Usage

Clone the repository:  
`git clone https://github.com/ui-1/nlet.git`

Run the script, specifying the amount of letters as the only argument:  
`python main.py 1`

## bonus

here's a meme i really like i hope you enjoy it too
![scraping is cool](meme.jpg)
source: https://twitter.com/gf_256/status/1514131084702797827