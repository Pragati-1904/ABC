from . import *
from .database.addwork_db import get_work, get_name_of_all_work, edit_work, is_work_present, rename_work, delete_work

@bot.on(events.NewMessage(incoming=True, pattern="^/tasks$"))
async def wrkks(event):
    if event.sender_id not in Var.ADMINS:
        return
    work_names = await get_name_of_all_work()
    if not work_names:
        return await event.reply("```No Tasks Found!```")
    _lst = [Button.inline(f"👨‍🏭 {x}", data=f"edwrk_{x}") for x in work_names]
    button = list(zip(_lst[::3], _lst[1::3], _lst[2::3]))
    button.append(
        [_lst[-(z + 1)] for z in reversed(range(len(_lst) - ((len(_lst) // 3) * 3)))]
    )
    await event.reply("```Choose Any Tasks From The Below Options:```", buttons=button)

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("bek")))
async def _wrkks(event):
    work_names = await get_name_of_all_work()
    if not work_names:
        return await event.edit("```No Tasks Found!```")
    _lst = [Button.inline(f"👨‍🏭 {x}", data=f"edwrk_{x}") for x in work_names]
    button = list(zip(_lst[::3], _lst[1::3], _lst[2::3]))
    button.append(
        [_lst[-(z + 1)] for z in reversed(range(len(_lst) - ((len(_lst) // 3) * 3)))]
    )
    await event.edit("```Choose Any Tasks From The Below Options:```", buttons=button)

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("edwrk_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    data = await get_work(wrk_name)
    frsd = "🚫 Show Forward Header" if not data.get("show_forward_header") else "✅ Show Forward Header"
    ben = "Enable Blacklist" if not data.get("has_to_blacklist") else "Disable Blacklist"
    een = "Enable Edit" if not data.get("has_to_edit") else "Disable Edit"
    button = [
        [
            Button.inline("Edit Name", data=f"ned_{wrk_name}"),
            Button.inline("Edit Delay", data=f"ded_{wrk_name}")
        ],
        [
            Button.inline("Edit Source", data=f"sed_{wrk_name}"),
            Button.inline("Edit Destination", data=f"ted_{wrk_name}")
        ],
        [
            Button.inline("Disable Forward", data=f"disfor_{wrk_name}"),
            Button.inline("Enable Forward", data=f"enfor_{wrk_name}")
        ],
        [
            Button.inline("Edit Blacklist", data=f"bled_{wrk_name}"),
            Button.inline(ben, data=f"bkhas_{wrk_name}")
        ],
        [Button.inline(een, data=f"ehas_{wrk_name}")],
        [Button.inline(frsd, data=f"hedfor_{wrk_name}")],
        [Button.inline("Delete This Task", data=f"delt_{wrk_name}")],
        [Button.inline("« BACK »", data=f"bek")]
    ]
    txt = f"**Information About {wrk_name}**\n\n"
    txt += f"**Forwarding Status**: ```{'RUNNING' if data.get('has_to_forward') else 'STOPPED'}```\n"
    txt += f"**Show Forward Header**: ```{'NO' if not data.get('show_forward_header') else 'YES'}```\n"
    txt += f"**Delay Of**: ```{data.get('delay')}s```\n"
    await e.edit(txt, buttons=button)

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("ned_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    try:
        async with bot.conversation(e.sender_id, timeout=2000) as conv:
            await e.delete()
            await conv.send_message(
                "Send New Name Of Current Task. You Can Send /cancel Anytime To Abort This Process."
            )
            try:
                new_wrk_name = (await conv.get_response()).text
                if new_wrk_name.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
            except BaseException:
                return await conv.send_message("Invalid Input")
            if (await is_work_present(new_wrk_name)):
                return await conv.send_message("Use Different Task Name.The Given Task Name is Already Present in Database")
            await rename_work(wrk_name, new_wrk_name)
            return await conv.send_message("Successfully Edited", buttons=[[Button.inline("« BACK »", data=f"edwrk_{new_wrk_name}")]])
    except TimeoutError:
        pass


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("ded_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    try:
        async with bot.conversation(e.sender_id, timeout=2000) as conv:
            await e.delete()
            await conv.send_message(
                "Send Delay Time of Forwarding Message In Seconds.\nEx - `120`.\nYou Can Send /cancel Anytime To Abort This Process."
            )
            res = (await conv.get_response()).text
            try:
                if res.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
                sec = int(res)
            except BaseException:
                return await conv.send_message("Invalid Input", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
            await edit_work(work_name=wrk_name, delay=sec)
            return await conv.send_message("Successfully Edited", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    except TimeoutError:
        pass
    

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("sed_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    try:
        async with bot.conversation(e.sender_id, timeout=2000) as conv:
            await e.delete()
            await conv.send_message(
                "Send Source Channel Id In One Message.\n__Make Sure Separated By a Space if Adding Multi Channels__.\nYou Can Send /cancel Anytime To Abort This Process.\n\nThe Following Source Channels In This Task are:\n```{}```".format('\n'.join(map(str, wrk_data.get('source'))))
            )
            res = await conv.get_response()
            try:
                if res.text.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
                source_chats = [int(i) for i in res.text.split()]
            except BaseException:
                return await conv.send_message("Invalid Input", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
            try:
                for schat in source_chats:
                    lol = await bot.get_entity(schat) 
            except BaseException:
                return await conv.send_message("Wrong Channel id", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
            await edit_work(work_name=wrk_name, source=source_chats)
            return await conv.send_message("Successfully Edited", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    except TimeoutError:
        pass


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("ted_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    try:
        async with bot.conversation(e.sender_id, timeout=2000) as conv:
            await e.delete()
            await conv.send_message(
                "Send Destination Channel Id In One Message.\n__Make Sure Separated By a Space if Adding Multi Channels__.\nYou Can Send /cancel Anytime To Abort This Process.\n\nThe Following Destination Channels In This Task are:\n```{}```".format('\n'.join(map(str, wrk_data.get('target'))))
            )
            res = await conv.get_response()
            try:
                if res.text.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
                target_chats = [int(i) for i in res.text.split()]
            except BaseException:
                return await conv.send_message("Invalid Input", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
            try:
                for dchat in target_chats:
                    lol = await bot.get_entity(dchat) 
            except BaseException:
                return await conv.send_message("Wrong Channel id", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
            await edit_work(work_name=wrk_name, target=target_chats)
            return await conv.send_message("Successfully Edited", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    except TimeoutError:
        pass

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("disfor_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    if wrk_data.get("has_to_forward"):
        await edit_work(work_name=wrk_name, has_to_forward=False)
        return await e.edit("Succesfully Disabled The Task", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    return await e.edit("The Task Is Already Disabled", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("enfor_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    if not wrk_data.get("has_to_forward"):
        await edit_work(work_name=wrk_name, has_to_forward=True)
        return await e.edit("Succesfully Enabled The Task", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    return await e.edit("The Task Is Already Enabled", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("hedfor_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    if wrk_data.get("show_forward_header"):
        await edit_work(work_name=wrk_name, show_forward_header=False)
        return await e.edit("Succesfully Disabled The Forward Header.", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    await edit_work(work_name=wrk_name, show_forward_header=True)
    return await e.edit("Succesfully Enabled The Forward Header.", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("delt_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    await delete_work(wrk_name)
    await e.edit("Succesfully Deleted The Task.", buttons=[[Button.inline("« BACK »", data=f"bek")]])

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("bled_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    try:
        async with bot.conversation(e.sender_id, timeout=2000) as conv:
            await e.delete()
            await conv.send_message(
                'Send Send Blacklist Words In One Message.\n__Make Sure Separated By a Space if Adding Multi Words__.\nYou Can Send /cancel Anytime To Abort This Process.\n\nThe Following Blacklisted Words In This Task are:\n```{}```'.format("\n".join(wrk_data.get("blacklist_words")))
            )
            res = await conv.get_response()
            try:
                if res.text.startswith("/cancel"):
                    return await conv.send_message("Proccess Aborted!", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
                blacklisted_words = [i.lower() for i in res.message.split()]
            except BaseException:
                return await conv.send_message("Invalid Input", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
            await edit_work(work_name=wrk_name, blacklist_words=blacklisted_words)
            return await conv.send_message("Successfully Edited", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    except TimeoutError:
        pass

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("bkhas_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    if wrk_data.get("has_to_blacklist"):
        await edit_work(work_name=wrk_name, has_to_blacklist=False)
        return await e.edit("Succesfully Disabled The Blacklist Filter.", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    await edit_work(work_name=wrk_name, has_to_blacklist=True)
    return await e.edit("Succesfully Enabled The Blacklist Filter.", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("ehas_(.*)")))
async def _(e):
    wrk_name = e.pattern_match.group(1).decode("utf-8")
    wrk_data = await get_work(wrk_name)
    if wrk_data.get("has_to_edit"):
        await edit_work(work_name=wrk_name, has_to_edit=False)
        return await e.edit("Succesfully Disabled The Edit Feature.", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])
    await edit_work(work_name=wrk_name, has_to_edit=True)
    return await e.edit("Succesfully Enabled The Edit Feature.", buttons=[[Button.inline("« BACK »", data=f"edwrk_{wrk_name}")]])