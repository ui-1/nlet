import aiohttp
import asyncio
import itertools
import string
from alive_progress import alive_bar
from yarl import URL
from http.cookies import BaseCookie
from bs4 import BeautifulSoup


async def test_username(username: str, session: aiohttp.ClientSession, auth_token: str) -> bool:
    inum = '0'
    headers = {'Content-Type': f'multipart/form-data; boundary=---------------------------{inum}'}
    data = f'-----------------------------{inum}\r\nContent-Disposition: form-data; name="authenticity_token"\r\n\r\n{auth_token}\r\n-----------------------------{inum}\r\nContent-Disposition: form-data; name="value"\r\n\r\n{username}\r\n-----------------------------{inum}--\r\n'

    async with session.post('/signup_check/username', data=data, headers=headers) as resp:
        message = await resp.text()
        if message == f'{username} is available.': return True
        else:
            print(f'{username} is not available')
            return False


async def session_setup(session: aiohttp.ClientSession) -> (BaseCookie[str], str):
    async with session.get('/signup') as resp:
        cookies = session.cookie_jar.filter_cookies(URL('https://github.com'))
        token = await extract_auth_token(await resp.text())
        return cookies, token


async def extract_auth_token(text: str) -> str:
    soup = BeautifulSoup(text, 'html.parser')
    res = soup.findAll('auto-check', src='/signup_check/username')
    return res[0].contents[3]['value']


async def generate_usernames(n: int) -> list:
    let = list(string.ascii_lowercase) + list(string.digits)
    names = [''.join(i) for i in itertools.product(let, repeat=n)]
    print(f'{len(names)} usernames to test')
    return names


async def worker(queue: asyncio.Queue) -> None:
    nt_cookies = None
    async with aiohttp.ClientSession('https://github.com/', cookies=nt_cookies) as nt_session:
        rc_cookies, token = await session_setup(nt_session)
        while True:
            name = await queue.get()
            res = await test_username(name, nt_session, token)
            if res:
                print(f'Username {name} is available!')
            queue.task_done()


async def progress_monitor(queue: asyncio.Queue) -> None:
    previous_size = queue.qsize()
    with alive_bar(previous_size) as bar:
        while True:
            await asyncio.sleep(.2)
            current_size = queue.qsize()
            queue_change = previous_size - current_size
            if queue_change: bar(queue_change)
            if current_size == 0: return
            previous_size = current_size


async def main(length: int, num_workers: int=1) -> None:
    names = await generate_usernames(length)

    queue = asyncio.Queue()
    for name in names: queue.put_nowait(name)

    workers = []
    for _ in range(num_workers):
        w = asyncio.create_task(worker(queue))
        workers.append(w)

    progressmon = asyncio.create_task(progress_monitor(queue))

    await queue.join()
    for w in workers: w.cancel()
    progressmon.cancel()


if __name__ == '__main__':
    asyncio.run(main(4))
