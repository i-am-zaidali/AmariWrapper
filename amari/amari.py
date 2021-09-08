import aiohttp
from cachetools import cachedmethod, TTLCache
from cachetools.keys import hashkey
import functools
import requests
from .Exceptions import *
from .datamodels import *

status_codes = {
    404: NotFoundError,
    429: RatelimitedError,
    500: APIError,
}

class AmariClient():
    def __init__(self, bot, auth_key:str):
        self.bot = bot
        self.url = "https://amaribot.com/api/v1/"
        self.auth_key = auth_key
        self.status_codes = []
        self.cache = TTLCache(100, 180)
        
        response = requests.get(self.url, headers={"Authorization": self.auth_key})
        if response.json().get("error") and response.json().get("error").lower() == "unauthorized":
            raise RuntimeError("Given Auth_key for the AmariAPI was invalid. Please head over to your Amari developer dashboard and get a proper authorization token.")

    @staticmethod
    def check_status_code(response):
        """Internal private method to check the status code to see the result is proper."""
        global status_codes
        if response.status in status_codes:
            raise status_codes[response.status](response.status)

    @cachedmethod(lambda self: self.cache, functools.partial(hashkey, "GuildUser"))
    async def getGuildUser(self, user_id:int, guild_id:int):
        """Get a AmariUser object by fetching it from the API

        Args:
            user_id (int): The user's id to get the object of.
            guild_id (int): The guild id where the user resides.

        Returns:
            AmariUser: An instance of `AmariUser`
        """
        data = await self.url_request(endpoint=f"guild/{guild_id}/member/{user_id}")
        return AmariUser(self.bot, data, self.bot.get_guild(int(guild_id)))
    
    @cachedmethod(lambda self: self.cache, functools.partial(hashkey, "GuildLeaderboard"))
    async def getGuildLeaderboard(self, guild_id:int, *, page:int=1, limit:int=50):
        """Get a guild's leaderboard. Each page is limites to a 1000 entries limit if the guild has more than 1000 members

        Args:
            guild_id (int): The guild id to get the leaderboard of.
            page (int, optional): The page number to get. Defaults to 1.
            limit (int, optional): The limit of each page. Maximum is 1000. Defaults to 50.

        Returns:
            [type]: [description]
        """
        if limit > 1000:
            raise ValueError("Limit can't be bigger than 1000.")
        data = await self.url_request(endpoint=f"guild/leaderboard/{guild_id}?page={page}&limit={limit}")
        return AmariLeaderboard(self.bot, data, self.bot.get_guild(int(guild_id)))
        
    async def getLeaderboardPosition(self, user_id:int, guild_id:int):
        """
        Get the leaderboard position of a user."""
        leaderboard = await self.getGuildLeaderboard(guild_id, limit=100)
        lb = leaderboard.get_leaderboard(100)
        
        for index, user in enumerate(lb, 1):
            if int(user.id) == int(user_id):
                return index, user
            
        raise ValueError(f"{user_id} is not present in the leaderboard")    
    
    @cachedmethod(lambda self: self.cache, functools.partial(hashkey, "GuildLeaderboard"))
    async def getCompleteLeaderboard(self, guild_id):
        """Get the complete leaderboard of a guild with all pages merged into one AmariLeaderboard object. 
        
        This can be a bit slow and get you ratelimited due to multiple API calls.

        Args:
            guild_id (int): the guild's id to get the leaderboard of.

        Returns:
            AmariLeaderboard: AmariLeaderboard instance.
        """
        main = AmariLeaderboard(self.bot, await self.url_request(endpoint=f"guild/leaderboard/{guild_id}?page=1&limit=1000"))
        if main.count != main.total_count:
            remaining = int(main.total_count/1000)
            for i in range(remaining):
                new = AmariLeaderboard(self.bot, await self.url_request(endpoint=f"guild/leaderboard/{guild_id}?page={i+2}&limit=1000"))
                main = main + new
            return main
        return main
    
    @cachedmethod(lambda self: self.cache, functools.partial(hashkey, "WeeklyLeaderboard"))
    async def getWeeklyLeaderboard(self, guild_id:int, *, page:int=1, limit:int=10):
        """Get a guild's weekly xp leaderboard.

        Args:
            guild_id (int): The guild's id.
            page (int, optional): The page number. Defaults to 1.
            limit (int, optional): Entry limit per page. Defaults to 10.

        Returns:
            AmariLeaderboard: Amarileaderboard instance.
        """
        data = await self.url_request(endpoint=f"guild/weekly/{guild_id}?page={page}&limit={limit}")
        return AmariLeaderboard(self.bot, data, self.bot.get_guild(int(guild_id)))
    
    @cachedmethod(lambda self: self.cache, functools.partial(hashkey, "GuildRewards"))
    async def getGuildRewards(self, guild_id:int, *, page:int=1, limit:int=10):
        """Get a guild's level role rewards.

        Args:
            guild_id (int): The guild's id
            page (int, optional): The page number. Defaults to 1.
            limit (int, optional): Entry limit per page. Defaults to 10.

        Returns:
            AmariRewards: AmariRewards instance.
        """
        data = await self.url_request(endpoint=f"guild/rewards/{guild_id}?page={page}&limit={limit}")
        return AmariRewards(data, self.bot.get_guild(int(guild_id)))
        
    async def url_request(self, *, endpoint=None):
        async with aiohttp.ClientSession(headers={"Authorization": self.auth_key}) as session:
            async with session.get(self.url+endpoint if endpoint else "") as response:
                self.check_status_code(response)
                return await response.json()