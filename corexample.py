import asyncio

loop = asyncio.get_event_loop()

async def worker(idx: int, que: asyncio.Queue):
    print(f'async run worker{idx}')
    while True:
        print(f'worker{idx} wait for item')
        item = await que.get()
        if item is None:
            que.task_done()
            break
        else:
            await asyncio.sleep(0.01)      # work
            que.task_done()
            print(f'worker{idx} -> item:{item}')

    print(f'worker{idx} finished')


async def producer(que: asyncio.Queue, num: int):
    print('producer: starting')
    for i in range(num * 10):
        await que.put(i)
        print(f'add task{i} into queue')

    print('producer: add end')
    for i in range(num):
        await que.put(None)
    await que.join()

def setup():
    queue = asyncio.Queue()
    global loop

    async def p_w_main():
        workers = [loop.create_task(worker(i, queue)) for i in range(10)]
        p = loop.create_task(producer(queue, 10))
        await asyncio.wait(workers + [p])

    loop.run_until_complete(p_w_main())

def update():
    ...

if __name__ == '__main__':
    setup()
