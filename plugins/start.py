import os, asyncio, humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait,ChatAdminRequired, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from bot import Bot
from config import *
from helper_func import subscribed, encode, decode, get_messages
from database.database import db
logger = logging.getLogger(__name__)
import time
import logging 
from lazydeveloperr.lazy_forcesub import is_subscribed, lazy_force_sub
import datetime
neha_delete_time = FILE_AUTO_DELETE
neha = neha_delete_time
file_auto_delete = humanize.naturaldelta(neha)

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user = message.from_user
    # if not await db.is_user_exist(user.id):
    #     await db.add_user(user.id)
    id = message.from_user.id
    if not await db.present_user(id):
        try:
            await db.add_user(id)
        except Exception as e:
            print(f"Error adding user: {e}")
            pass

    if (FORCE_SUB_CHANNEL or FORCE_SUB_CHANNEL2 or FORCE_SUB_CHANNEL3) and not await is_subscribed(client, message):
        # User is not subscribed to any of the required channels, trigger force_sub logic
        return await lazy_force_sub(client, message)
        
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except IndexError:
            return

        string = await decode(base64_string)
        argument = string.split("-")
        
        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        temp_msg = await message.reply("Wait A Sec..")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something Went Wrong..!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        lazy_msgs = []  # List to keep track of sent messages

        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                             filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                lazy_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                lazy_msgs.append(copied_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")
                pass

        k = await client.send_message(chat_id=message.from_user.id, 
                                      text=f"<b><i>This File is deleting automatically in {file_auto_delete}. Forward in your Saved Messages..!</i></b>")

        # Schedule the file deletion
        asyncio.create_task(delete_files(lazy_msgs, client, k))

        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⚡️ ᴍᴏᴠɪᴇs', url='https://t.me/moviesimplyfytuber'),
                    InlineKeyboardButton('🍁 ᴄʀɪᴄᴋᴇᴛ ɴᴇᴡꜱ​​​​​', url='https://telegram.me/cricketediting')
                ],
                [
                    InlineKeyboardButton('🍿.  ꜰʀᴇᴇ ᴀᴘᴘꜱ​  .🚀', url='https://telegram.me/simplifytuberyt')
                ]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return

# @Bot.on_message(filters.command('start') & filters.private)
# async def not_joined(client: Client, message: Message):
#     try:
#         invite_link = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL), creates_join_request=True)
#         invite_link2 = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL2), creates_join_request=True)
#         invite_link3 = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL3), creates_join_request=True)
#     except ChatAdminRequired:
#         logger.error("Hey Sona, Ek dfa check kr lo ki auth Channel mei Add hu ya nhi...!")
#         return
#     buttons = [
#         [
#             InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ1", url=invite_link.invite_link),
#             InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ2", url=invite_link2.invite_link),
#             InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ3", url=invite_link3.invite_link),
#         ]
#     ]
#     try:
#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text='ʀᴇʟᴏᴀᴅ',
#                     url=f"https://t.me/{client.username}?start={message.command[1]}"
#                 )
#             ]
#         )
#     except IndexError:
#         pass

#     await message.reply(
#         text=FORCE_MSG.format(
#             first=message.from_user.first_name,
#             last=message.from_user.last_name,
#             username=None if not message.from_user.username else '@' + message.from_user.username,
#             mention=message.from_user.mention,
#             id=message.from_user.id
#         ),
#         reply_markup=InlineKeyboardMarkup(buttons),
#         quote=True,
#         disable_web_page_preview=True
#     )

# @Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
# async def get_users(client: Bot, message: Message):
#     msg = await client.send_message(chat_id=message.chat.id, text=f"Processing...")

#     users = await db.full_userbase()
#     await msg.edit(f"{len(users)} Users Are Using This Bot")

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text="Processing...")

    try:
        # Fetch all user IDs from the database
        users = await db.full_userbase()
        user_count = len(users)

        # Update the message with the count
        await msg.edit(f"✅ {user_count} Users Are Using This Bot")
    except Exception as e:
        # Handle potential errors
        print(f"Error fetching user data: {e}")
        await msg.edit("❌ Failed to fetch user data. Please try again later.")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        print(f'Broadcast hit me')
        query = await db.full_userbase()
        broadcast_msg = message.reply_to_message
        total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0

        pls_wait = await message.reply("<i>Broadcasting Message... This will Take Some Time</i>")
        
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await db.del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await db.del_user(chat_id)
                deleted += 1
            except Exception as e:
                print(f"Failed to send message to {chat_id}: {e}")
                unsuccessful += 1
            total += 1

            # Periodic update every 100 messages
            if total % 100 == 0:
                await pls_wait.edit(f"<i>Broadcasting...</i>\n\n<b>Total Processed:</b> <code>{total}</code>")

        status = f"""<b><u>Broadcast Completed</u></b>

<b>Total Users :</b> <code>{total}</code>
<b>Successful :</b> <code>{successful}</code>
<b>Blocked Users :</b> <code>{blocked}</code>
<b>Deleted Accounts :</b> <code>{deleted}</code>
<b>Unsuccessful :</b> <code>{unsuccessful}</code>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply("Use this command as a reply to any Telegram message.")
        await asyncio.sleep(8)
        await msg.delete()


# @Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
# async def send_text(client: Bot, message: Message):
#     if message.reply_to_message:
#         query = await db.full_userbase()
#         broadcast_msg = message.reply_to_message
#         total = 0
#         successful = 0
#         blocked = 0
#         deleted = 0
#         unsuccessful = 0
        
#         pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
#         for chat_id in query:
#             try:
#                 await broadcast_msg.copy(chat_id)
#                 successful += 1
#             except FloodWait as e:
#                 await asyncio.sleep(e.x)
#                 await broadcast_msg.copy(chat_id)
#                 successful += 1
#             except UserIsBlocked:
#                 await db.del_user(chat_id)
#                 blocked += 1
#             except InputUserDeactivated:
#                 await db.del_user(chat_id)
#                 deleted += 1
#             except Exception as e:
#                 print(f"Failed to send message to {chat_id}: {e}")
#                 unsuccessful += 1
#                 pass
#             total += 1
        
#         status = f"""<b><u>Broadcast Completed</u></b>

# <b>Total Users :</b> <code>{total}</code>
# <b>Successful :</b> <code>{successful}</code>
# <b>Blocked Users :</b> <code>{blocked}</code>
# <b>Deleted Accounts :</b> <code>{deleted}</code>
# <b>Unsuccessful :</b> <code>{unsuccessful}</code>"""
        
#         return await pls_wait.edit(status)

#     else:
#         msg = await message.reply(f"Use This Command As A Reply To Any Telegram Message Without Any Spaces.")
#         await asyncio.sleep(8)
#         await msg.delete()


# @Bot.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
# async def broadcast_handler(bot: Client, m: Message):
#     all_users = await db.get_all_users()
#     broadcast_msg = m.reply_to_message
#     sts_msg = await m.reply_text("broadcast started !") 
#     done = 0
#     failed = 0
#     success = 0
#     start_time = time.time()
#     total_users = await db.total_users_count()
#     async for user in all_users:
#         sts = await send_msg(user['_id'], broadcast_msg)
#         if sts == 200:
#            success += 1
#         else:
#            failed += 1
#         if sts == 400:
#            await db.delete_user(user['_id'])
#         done += 1
#         if not done % 20:
#            await sts_msg.edit(f"Broadcast in progress:\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")
#     completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
#     await sts_msg.edit(f"Broadcast Completed:\nCompleted in `{completed_in}`.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")
           
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : deactivated")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : blocked the bot")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : user id invalid")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500
 

# Function to handle file deletion
async def delete_files(messages, client, k):
    await asyncio.sleep(FILE_AUTO_DELETE)  # Wait for the duration specified in config.py
    
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"The attempt to delete the media {msg.id} was unsuccessful: {e}")

    # Safeguard against k.command being None or having insufficient parts
    command_part = k.command[1] if k.command and len(k.command) > 1 else None

    if command_part:
        button_url = f"https://t.me/{client.username}?start={command_part}"
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=button_url)]
            ]
        )
    else:
        keyboard = None

    # Edit message with the button
    await k.edit_text("<b><i>Your Video / File Is Successfully Deleted ✅</i></b>", reply_markup=keyboard)
