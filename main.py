import aiohttp
import asyncio
import itertools
import string
import sys
import re
from alive_progress import alive_bar
from bs4 import BeautifulSoup


async def username_available(username: str, session: aiohttp.ClientSession, auth_token: str) -> bool:
    headers = {'Content-Type': 'multipart/form-data; boundary=---------------------------'}
    data = '-----------------------------\r\nContent-Disposition: form-data; name="authenticity_token"\r\n\r\n' \
           f'{auth_token}\r\n-----------------------------\r\nContent-Disposition: form-data; name="value"\r\n\r\n' \
           f'{username}\r\n-------------------------------\r\n'

    async with session.post('/signup_check/username', data=data, headers=headers) as response:
        message = await response.text()
        return True if message == f'{username} is available.' else False


async def get_token(session: aiohttp.ClientSession) -> str:
    async with session.get('/signup') as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        result = soup.findAll('auto-check', src='/signup_check/username')
        return result[0].contents[3]['value']


async def generate_usernames(n: int) -> list:
    # Strategy: generate all n-letter combinations of a-z + 0-9 + '-'
    # and then remove the few that are not valid usernames
    letters = list(string.ascii_lowercase) + list(string.digits) + ['-']
    usernames = [''.join(i) for i in itertools.product(letters, repeat=n)]
    github_username_pattern = re.compile('^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$')
    usernames = [u for u in usernames if github_username_pattern.match(u) is not None]
    usernames.sort()
    print(f'Generated {len(usernames)} usernames')
    return usernames


async def worker(queue: asyncio.Queue) -> None:
    async with aiohttp.ClientSession('https://github.com/') as session:
        token = await get_token(session)
        while queue.qsize() != 0:
            username = await queue.get()
            if await username_available(username, session, token):
                print(f'Username \'{username}\' is available!')
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


async def main(num_workers: int=512) -> None:
    try:
        assert len(sys.argv) == 2
        assert sys.argv[1].isnumeric() and 39 >= int(sys.argv[1]) >= 1
    except AssertionError:
        raise SystemExit(f'Usage: {sys.argv[0]} <username length (1 <= n <= 39)>')

    usernames = await generate_usernames(int(sys.argv[1]))

    queue = asyncio.Queue()
    for u in usernames: queue.put_nowait(u)

    workers = []
    for _ in range(num_workers):
        w = asyncio.create_task(worker(queue))
        workers.append(w)

    progressmon = asyncio.create_task(progress_monitor(queue))

    await queue.join()
    for w in workers: w.cancel()
    progressmon.cancel()


if __name__ == '__main__':
    asyncio.run(main())
