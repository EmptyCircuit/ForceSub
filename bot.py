import logging
from telethon.utils import get_display_name
import re
import asyncio
import random
from telethon import TelegramClient, events, Button
from decouple import config
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.INFO
)
log = logging.getLogger("ForceSubBot")

# Bot Configuration
log.info("Initializing Force Subscription Bot...")
try:
    bottoken = config("BOT_TOKEN")
    xchannel = config("CHANNEL")
    welcome_not_joined = config("WELCOME_NOT_JOINED")
except Exception as e:
    log.error(f"Configuration Error: {e}")
    exit()

try:
    Cypherix = TelegramClient("ForceSubBot", 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e").start(
        bot_token=bottoken
    )
except Exception as e:
    log.error(f"Startup Error: {str(e)}")
    exit()

channel = xchannel.replace("@", "")
bot_self = Cypherix.loop.run_until_complete(Cypherix.get_me())

# Track subscribed and muted users
subscribed_users = {}
muted_users = set()

async def get_user_join(user_id):
    try:
        await Cypherix(GetParticipantRequest(channel=channel, participant=user_id))
        return True
    except UserNotParticipantError:
        return False

@Cypherix.on(events.ChatAction)
async def handle_new_members(event):
    if not event.is_group or not (event.user_joined or event.user_added):
        return

    user = await event.get_user()
    chat = await event.get_chat()

    mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
    is_subscribed = await get_user_join(user.id)

    if is_subscribed:
        subscribed_users[user.id] = event.chat.id
        if user.id in muted_users:
            msg = (f"😊 Welcome back, {mention}! 🎉 You're now unmuted and happy to see you again "
                   f"in {chat.title}! 🚀")
            await Cypherix.edit_permissions(event.chat.id, user.id, send_messages=True)
            muted_users.remove(user.id)
        else:
            msg = (f"😊 Welcome to Cypherix, {mention}! 🎉 You're now unmuted and ready to chat in "
                   f"{chat.title}! 🚀")
        buttons = [Button.url("Visit Channel", url=f"https://t.me/{channel}")]
    else:
        username = f"@{user.username}" if user.username else mention
        msg = welcome_not_joined.format(mention=mention, username=username, channel=f"@{channel}")
        buttons = [
            [Button.url("🔥 Join Cypherix Now", url=f"https://t.me/{channel}")],
            [Button.inline("✅ Verify Subscription", data=f"unmute_{user.id}")]
        ]
        await Cypherix.edit_permissions(event.chat.id, user.id, send_messages=False)

    await event.reply(msg, buttons=buttons)

@Cypherix.on(events.callbackquery.CallbackQuery(data=re.compile(b"unmute_(.*)")))
async def handle_unmute(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid != event.sender_id:
        return await event.answer("This button is not for you!", cache_time=0, alert=True)

    if await get_user_join(uid):
        subscribed_users[uid] = event.chat_id
        await Cypherix.edit_permissions(event.chat_id, uid, send_messages=True)
        if uid in muted_users:
            msg = (f"😊 Welcome back, [User](tg://user?id={uid})! 🎉 You're now unmuted in "
                   f"{event.chat.title}! 🚀")
            muted_users.discard(uid)
        else:
            msg = (f"😊 Welcome to Cypherix, [User](tg://user?id={uid})! 🎉 You're now unmuted and ready to "
                   f"chat in {event.chat.title}! 🚀")
        await event.edit(msg, buttons=[Button.url("Visit Channel", url=f"https://t.me/{channel}")])
    else:
        await event.answer(f"Please join @{channel} first!", cache_time=0, alert=True)

@Cypherix.on(events.NewMessage(pattern="^/start$"))
async def start(event):
    await event.reply(
        "🔒 Access restricted! Join Cypherix to proceed.",
        buttons=[[Button.url("🔥 Join Cypherix Now", url=f"https://t.me/{channel}")]],
    )

# Background task to check for unsubscribed users every 1-2 seconds
async def check_unsubscribed():
    while True:
        await asyncio.sleep(random.uniform(1, 2))
        for user_id, chat_id in list(subscribed_users.items()):
            if not await get_user_join(user_id):
                log.info(f"User {user_id} unsubscribed, muting them...")
                try:
                    await Cypherix.edit_permissions(chat_id, user_id, send_messages=False)
                    muted_users.add(user_id)
                except Exception as e:
                    log.error(f"Failed to mute user {user_id}: {str(e)}")
            elif user_id in muted_users:
                log.info(f"User {user_id} resubscribed, unmuting them...")
                try:
                    await Cypherix.edit_permissions(chat_id, user_id, send_messages=True)
                    muted_users.remove(user_id)
                except Exception as e:
                    log.error(f"Failed to unmute user {user_id}: {str(e)}")

Cypherix.loop.create_task(check_unsubscribed())

log.info(f"ForceSub Bot is now active as @{bot_self.username}. 🚀")
Cypherix.run_until_disconnected() which port
