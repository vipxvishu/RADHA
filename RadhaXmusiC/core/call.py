import asyncio
from datetime import datetime, timedelta

from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

from pyrogram.errors import (
    UserAlreadyParticipant,
    UserNotParticipant,
    ChannelInvalid,
    PeerIdInvalid,
    ChatAdminRequired,
    TelegramServerError,
    InviteRequestSent,
    AlreadyJoinedError,
    FloodWait,
    UserBannedInChannel,
)

from RadhaXmusiC import app, LOGGER, YouTube
from RadhaXmusiC.misc import db
from config import LOG_GROUP_ID

from RadhaXmusiC.utils.database import (
    add_active_chat,
    remove_active_chat,
    get_loop,
    set_loop,
    is_autoend,
    music_on,
    add_active_video_chat,
    remove_active_video_chat,
    group_assistant,
    get_lang,
)

from RadhaXmusiC.utils.exceptions import AssistantErr
from RadhaXmusiC.utils.formatters import seconds_to_min
from RadhaXmusiC.utils.inline.play import stream_markup
from RadhaXmusiC.utils.stream.autoclear import auto_clean
from RadhaXmusiC.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}


class Call:
    def __init__(self):
        self.client = PyTgCalls(app, cache_duration=100, overload_qualify=True)
        self.client.on_stream_end()(self.on_stream_end)

    async def start(self):
        await self.client.start()
        LOGGER("RadhaXmusiC").info("Group Call Client Started")

    async def join_call(self, message, file, chat_id, video=False):
        try:
            if video:
                await self.client.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        file,
                        HighQualityAudio(),
                        MediumQualityVideo(),
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                await add_active_video_chat(chat_id)
            else:
                await self.client.join_group_call(
                    chat_id,
                    AudioPiped(file, HighQualityAudio()),
                    stream_type=StreamType().pulse_stream,
                )
                await add_active_chat(chat_id)
            await music_on(chat_id)
        except Exception as e:
            LOGGER("RadhaXmusiC").error(f"Error joining call: {e}")
            raise AssistantErr(e)

    async def change_stream(self, chat_id, file, video=False):
        try:
            if video:
                await self.client.change_stream(
                    chat_id,
                    AudioVideoPiped(
                        file,
                        HighQualityAudio(),
                        MediumQualityVideo(),
                    ),
                )
            else:
                await self.client.change_stream(
                    chat_id,
                    AudioPiped(file, HighQualityAudio()),
                )
        except Exception as e:
            LOGGER("RadhaXmusiC").error(f"Error changing stream: {e}")
            raise AssistantErr(e)

    async def leave(self, chat_id):
        try:
            await self.client.leave_group_call(chat_id)
        except Exception as e:
            LOGGER("RadhaXmusiC").warning(f"Error leaving call: {e}")
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)
        autoend.pop(chat_id, None)

    async def mute(self, chat_id):
        try:
            await self.client.mute_stream(chat_id)
        except Exception:
            pass

    async def unmute(self, chat_id):
        try:
            await self.client.unmute_stream(chat_id)
        except Exception:
            pass

    async def pause_stream(self, chat_id):
        try:
            await self.client.pause_stream(chat_id)
        except Exception:
            pass

    async def resume_stream(self, chat_id):
        try:
            await self.client.resume_stream(chat_id)
        except Exception:
            pass

    async def on_stream_end(self, _, update: Update):
        if isinstance(update, StreamAudioEnded):
            chat_id = update.chat_id
            db.reset(chat_id)
            from RadhaXmusiC.core.call import stop_stream
            await stop_stream(chat_id)
