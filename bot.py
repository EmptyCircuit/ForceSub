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
            msg = f"""
            ━━━━━━😈━━━━━━
            👋 ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, {mention}!
            🎭 ʏᴏᴜ'ᴠᴇ ʀᴇᴇɴᴛᴇʀᴇᴅ ᴛʜᴇ ᴄʜᴀᴏs.
            🚀 ᴜɴᴍᴜᴛᴇᴅ ɪɴ {chat.title} – ɴᴏ ᴇsᴄᴀᴘᴇ ɴᴏᴡ!
            ━━━━━━😈━━━━━━
            """
            await Cypherix.edit_permissions(event.chat.id, user.id, send_messages=True)
            muted_users.remove(user.id)
        else:
            msg = f"""
            ━━━━━━🔥━━━━━━
            👋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴍᴀᴅʜᴏᴜsᴇ, {mention}!
            🎭 ᴛʜᴇʀᴇ ɪs ɴᴏ ɢᴏɪɴɢ ʙᴀᴄᴋ ɴᴏᴡ...
            🚀 ᴇɴᴊᴏʏ ᴄʜᴀᴏs ɪɴ {chat.title}!
            ━━━━━━🔥━━━━━━
            """
        buttons = [Button.url("🔗 ʙᴇʜᴏʟᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{channel}")]
    else:
        username = f"@{user.username}" if user.username else mention
        msg = f"""
        ━━━━━━❌━━━━━━
        ⚠️ {mention}, ᴡʜᴏᴀ ʜᴏʟᴅ ᴜᴘ!
        ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ꜱɴᴇᴀᴋ ɪɴ, ʙᴜᴛ ᴛʜᴀᴛ'ꜱ ɪʟʟᴇɢᴀʟ ʜᴇʀᴇ. 😂
        📌 **ꜰɪʀꜱᴛ, ᴊᴏɪɴ ᴏᴜʀ ʟᴇɢᴇɴᴅᴀʀʏ ᴄʜᴀɴɴᴇʟ.**
        🔗 **@{channel}** – ᴏʀ ꜰᴀᴄᴇ ᴛʜᴇ ᴄᴏɴꜱᴇǫᴜᴇɴᴄᴇꜱ! 😈
        ━━━━━━❌━━━━━━
        """
        buttons = [
            [Button.url("🔥 ᴊᴏɪɴ ᴄʏᴘʜᴇʀɪx", url=f"https://t.me/{channel}")],
            [Button.inline("✅ ᴀᴜᴛᴏ-ᴠᴇʀɪꜰʏ ☑️", data=f"unmute_{user.id}")]
        ]
        await Cypherix.edit_permissions(event.chat.id, user.id, send_messages=False)

    sent_msg = await event.reply(msg, buttons=buttons)
    await asyncio.sleep(50)  # Auto-delete after 30 seconds
    await sent_msg.delete()

@Cypherix.on(events.callbackquery.CallbackQuery(data=re.compile(b"unmute_(.*)")))
async def handle_unmute(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid != event.sender_id:
        return await event.answer("🚫 ɴᴏᴛ ʏᴏᴜʀ ʙᴜᴛᴛᴏɴ, ᴍʏ ꜰʀɪᴇɴᴅ!", cache_time=0, alert=True)

    if await get_user_join(uid):
        subscribed_users[uid] = event.chat_id
        await Cypherix.edit_permissions(event.chat_id, uid, send_messages=True)
        msg = f"""
        🎉 ᴄᴏɴɢʀᴀᴛꜱ, [ᴜꜱᴇʀ](tg://user?id={uid})!
        🎭 ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ **ᴜɴʟᴏᴄᴋᴇᴅ** ꜰʀᴏᴍ ꜱɪʟᴇɴᴄᴇ.
        🚀 ɴᴏᴡ, ᴇɴᴊᴏʏ ᴛʜᴇ ᴄʜᴀᴏꜱ!
        """
        sent_msg = await event.edit(msg, buttons=[Button.url("🔗 ᴠɪꜱɪᴛ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{channel}")])
        await asyncio.sleep(30)  # Auto-delete after 10 seconds
        await sent_msg.delete()
    else:
        await event.answer(f"⚠️ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ @{channel} ʏᴇᴛ!", cache_time=0, alert=True)

log.info(f"ForceSub Bot is now active as @{bot_self.username}. 🚀")
Cypherix.run_until_disconnected()
