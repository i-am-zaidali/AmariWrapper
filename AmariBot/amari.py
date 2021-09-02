import aiohttp
from discord import guild
import requests
from .Exceptions import *
from .datamodels import *

status_codes = {
    404: NotFoundError,
    429: RatelimitedError,
    500: APIError,
}

class AmariClient():
    def __init__(self, bot, auth_key:str, enable_cache:bool):
        self.bot = bot
        self.url = "https://amaribot.com/api/v1/"
        self.auth_key = auth_key
        self.cache_enabled = enable_cache
        self.status_codes = []
        
        response = requests.get(self.url, headers={"Authorization": self.auth_key})
        if response.json().get("error") and response.json().get("error").lower() == "unauthorized":
            raise RuntimeError("Given Auth_key for the AmariAPI was invalid. Please head over to your Amari developer dashboard and get a proper authorization token.")

    @staticmethod
    def check_status_code(response):
        global status_codes
        if response.status in status_codes:
            raise status_codes[response.status](response.status)

    async def getGuildUser(self, user_id:int, guild_id:int):
        data = await self.url_request(endpoint=f"guild/{guild_id}/member/{user_id}")
        return AmariUser(self.bot, data, self.bot.get_guild(int(guild_id)))
    
    async def getGuildLeaderboard(self, guild_id:int, *, page:int=1, limit:int=10):
        data = await self.url_request(endpoint=f"guild/leaderboard/{guild_id}?page={page}&limit={limit}")
        return AmariLeaderboard(self.bot, data, self.bot.get_guild(int(guild_id)))
        
    async def getLeaderboardPosition(self, user_id:int, guild_id:int):
        leaderboard = await self.getGuildLeaderboard(guild_id, limit=100)
        lb = leaderboard.get_leaderboard(100)
        
        for index, user in enumerate(lb, 1):
            if int(user.id) == int(user_id):
                return index, user
            
        # raise ValueError(f"{user_id} is not present in the leaderboard")    
    async def getWeeklyLeaderboard(self, guild_id:int, *, page:int=1, limit:int=10):
        data = await self.url_request(endpoint=f"guild/weekly/{guild_id}?page={page}&limit={limit}")
        return AmariLeaderboard(self.bot, data, self.bot.get_guild(int(guild_id)))
    
    async def getGuildRewards(self, guild_id:int, *, page:int=1, limit:int=10):
        data = await self.url_request(endpoint=f"guild/rewards/{guild_id}?page={page}&limit={limit}")
        return AmariRewards(data, self.bot.get_guild(int(guild_id)))

    async def get_or_fetch_member(self, member_id:int):
        if member := self.bot.get_member(member_id):
            return member
        return await self.bot.fetch_member(member_id)
        
    async def url_request(self, *, endpoint=None):
        async with aiohttp.ClientSession(headers={"Authorization": self.auth_key}) as session:
            async with session.get(self.url+endpoint if endpoint else "") as response:
                self.check_status_code(response)
                return await response.json()