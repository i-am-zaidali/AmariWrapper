import aiohttp
import asyncio

from cache import AsyncTTL
from .Exceptions import *
from .datamodels import *

status_codes = {
    404: NotFoundError,
    429: RatelimitedError,
    500: APIError,
}

class AmariClient:
    
    URL = "https://amaribot.com/api/v1/"
    def __init__(self, bot, auth_key:str):
        self.bot = bot
        self.auth_key = auth_key
        self.status_codes = []
        self.session = aiohttp.ClientSession(headers={"Authorization": auth_key})
        
    def __del__(self):
        asyncio.get_event_loop().create_task(self.session.close())

    @staticmethod
    def check_status_code(response):
        """Internal private method to check the status code to see the result is proper."""
        global status_codes
        if response.status in status_codes:
            raise status_codes[response.status](response.status)

    @AsyncTTL(time_to_live=60, maxsize=60)
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
    
    @AsyncTTL(time_to_live=60, maxsize=60)
    async def getGuildUsers(self, guild_id:int, *members):
        """Get a list of AmariUser objects by fetching it from the API

        Args:
            guild_id (int): The guild id to get the users of.

        Returns:
            List[AmariUser]: A list of AmariUser objects. Sorted by their level and xp
        """
        data = await self.url_request(endpoint=f"guild/{guild_id}/members", method="POST", json={"members": members})
        guild = self.bot.get_guild(int(guild_id))
        return [AmariUser(self.bot, user, guild) for user in data["members"]]
    
    @AsyncTTL(time_to_live=60, maxsize=60)
    async def getGuildLeaderboard(self, guild_id:int, *, page:int=1, limit:int=50):
        """Get a guild's leaderboard. Each page is limited to a 1000 entries limit if the guild has more than 1000 members

        Args:
            guild_id (int): The guild id to get the leaderboard of.
            page (int, optional): The page number to get. Defaults to 1.
            limit (int, optional): The limit of each page. Maximum is 1000. Defaults to 50.

        Returns:
            AmariLeaderboard: An instance of Amarileaderboard
        """
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
    
    @AsyncTTL(time_to_live=60, maxsize=60)
    async def getCompleteLeaderboard(self, guild_id):
        """Get the complete leaderboard of a guild with all pages merged into one AmariLeaderboard object. 
        
        This can be a bit slow and get you ratelimited due to multiple API calls.

        Args:
            guild_id (int): the guild's id to get the leaderboard of.

        Returns:
            AmariLeaderboard: AmariLeaderboard instance.
        """
        guild = self.bot.get_guild(int(guild_id))
        org = await self.getGuildUsers(guild_id, *[str(member.id) for member in guild.members])
        org.sort(key=lambda x: (x.level, x.xp), reverse=True)
        return org
        # main = AmariLeaderboard(self.bot, await self.url_request(endpoint=f"guild/raw/leaderboard/{guild_id}"))
        # return main
    
    @AsyncTTL(time_to_live=60, maxsize=60)
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
    
    @AsyncTTL(time_to_live=60, maxsize=60)
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
        
    async def url_request(self, *, endpoint="", json=None, method="GET", headers={}):
        async with self.session as session:
            async with session.request(method=method, url=self.URL + endpoint, json=json, headers=headers) as response:
                self.check_status_code(response)
                return await response.json()