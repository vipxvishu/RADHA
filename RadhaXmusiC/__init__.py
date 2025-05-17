from RadhaXmusiC.core.bot import Anony
from RadhaXmusiC.core.dir import dirr
from RadhaXmusiC.core.git import git
from RadhaXmusiC.core.userbot import Userbot
from RadhaXmusiC.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Anony()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
