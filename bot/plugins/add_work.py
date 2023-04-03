from . import *
from .database.addwork_db import setup_work, is_work_present

@bot.on(events.NewMessage(incoming=True, pattern="^/addtask$"))
async def adwrk(event):
    if event.sender_id not in Var.ADMINS:
        return
    try:
        async with bot.conversation(event.sender_id, timeout=2000) as conv:
            await conv.send_message(
                "Process Started. You Can Send /cancel Anytime To Abort This Process.\n__And Ensure That The Bot is Admin The Both The Target And Source Channel.__"
            )
            await conv.send_message("Send The Name Of Task")
            try:
                wrk_name = (await conv.get_response()).text
                if wrk_name.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!")
            except BaseException:
                return await conv.send_message("Invalid Input")
            if (await is_work_present(wrk_name)):
                return await conv.send_message("Use Different Task Name.The Given Task Name is Already Present in Database")
            await conv.send_message(
                "Send Source Channel Id In One Message.\n__Make Sure Separated By a Space If Adding Multi Channels__"
            )
            res = await conv.get_response()
            try:
                if res.text.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!")
                source_chats = [int(i) for i in res.text.split()]
            except BaseException:
                return await conv.send_message("Invalid Input")
            try:
                for schat in source_chats:
                    lol = await bot.get_entity(schat) 
            except BaseException:
                return await conv.send_message("Wrong Channel id")
            await conv.send_message(
                "Send Destination or Target Channel Id In One Message.\n__Make Sure Separated By a Space If Adding Multi Channels__"
            )
            res_2 = await conv.get_response()
            try:
                if res_2.text.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!")
                desti_chats = [int(i) for i in res_2.text.split()]
            except BaseException:
                return await conv.send_message("Invalid Input")
            try:
                for dchat in desti_chats:
                    lolx = await bot.get_entity(dchat) 
            except BaseException:
                return await conv.send_message("Wrong Channel id")
            await setup_work(work_name=wrk_name, source=source_chats, target=desti_chats)
            return await conv.send_message("Added Successfully. For Further Update You Can Do /tasks")
    except TimeoutError:
        pass