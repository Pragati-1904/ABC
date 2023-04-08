from . import *
from .database.addwork_db import get_target_chat_with_data, edit_work
from telethon.utils import get_peer_id


async def forward(e, task):
    if task.get("delay"):
        await asyncio.sleep(task["delay"])
    target_chats = task["target"]
    cross_ids = task["crossids"]
    bl_words = task["blacklist_words"]
    head = True if task.get("show_forward_header") else False
    bl = True if task.get("has_to_blacklist") else False
    for chat in target_chats:
        try:
            if bl:
                if any((bl_word in word.lower()) for (word, bl_word) in (e.message.message.split(), bl_words)):
                    continue
            if head:
                await e.message.forward_to(chat)
            else:
                msg = await e.client.send_message(chat, e.message)
                if e.chat_id not in cross_ids:
                    cross_ids.update({e.chat_id: {e.id :{chat: msg.id}}})
                else:
                    data = cross_ids[e.chat_id]
                    if not data.get(e.id):
                        data.update({e.id: {chat: msg.id}})
                        cross_ids[e.chat_id] = data
                    else:
                        _data = cross_ids[e.chat_id][e.id]
                        _data.update({chat: msg.id})
                        cross_ids[e.chat_id][e.id] = _data 
                await edit_work(task["work_name"], crossids=cross_ids)
        except BaseException:
            pass

@bot.on(events.NewMessage(incoming=True))
async def fwder(e):
    ch = await e.get_chat()
    chat_id = get_peer_id(ch)
    tasks = await get_target_chat_with_data(chat_id)
    for task in tasks:
        if task.get("has_to_forward"):
            asyncio.ensure_future(forward(e, task))

@bot.on(events.MessageEdited(incoming=True))
async def msgedit(e: events.MessageEdited.Event):
    ch = await e.get_chat()
    chat_id = get_peer_id(ch)
    tasks = await get_target_chat_with_data(chat_id)
    for task in tasks:
        if task.get("has_to_edit"):
            asyncio.ensure_future(msgedit(e, task))

async def msgedit(e, task):
    cross_ids = task["crossids"]
    data = cross_ids[e.chat_id][e.id]
    for chat in data.keys():
        try:
            msg = await bot.get_messages(chat, ids=data[chat])
            await msg.edit(e.text)
        except BaseException:
            pass