from bot import dB, CACHE


async def get_work(work: str):
    return CACHE.get(work) or {}


async def setup_work(work_name: str, source: list, target: list):
    data = {
        "work_name": work_name,
        "source": source,
        "target": target,
        "show_forward_header": False,
        "delay": 0,
        "blacklist_words": [],
        "crossids": {},
        "has_to_edit": False,
        "has_to_blacklist": False,
        "has_to_forward": True
    }
    CACHE.update({work_name: data})
    return await dB.set(work_name, str(data))


async def get_target_chat_with_data(id: int):
    dst = []
    for work in CACHE.keys():
        if id in (CACHE[work].get("source") or []):
            dst.append(CACHE[work])
    return dst

async def edit_work(work_name: str, *args, **kwargs):
    raw_data = await get_work(work_name)
    if not raw_data:
        return False
    for key in kwargs.keys():
        raw_data[key] = kwargs[key]
    CACHE.update({work_name: raw_data})
    return await dB.set(work_name, str(raw_data))

async def delete_work(work_name: str):
    if work_name in CACHE:
        CACHE.pop(work_name)
    return await dB.delete(work_name)


async def is_work_present(work_name: str):
    data = await get_work(work_name)
    if data:
        return True
    return False


async def get_name_of_all_work():
    return CACHE.keys()


async def rename_work(work_name: str, new_work_name: str):
    if work_name in CACHE:
        data = CACHE.get(work_name)
        CACHE.pop(work_name)
        CACHE.update({new_work_name: data})
    return await dB.rename(work_name, new_work_name)
