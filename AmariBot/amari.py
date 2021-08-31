import aiohttp
import requests
import datamodels

class AmariClient():
    def __init__(self, bot, auth_key:str, enable_cache:bool):
        self.bot = bot
        self.url = "https://amaribot.com/api/v1/"
        self.auth_key = auth_key
        self.cache_enabled = enable_cache
        
        response = requests.get(self.url, headers={"Authorization": self.auth_key})
        if response.json().get("error") and response.json().get("error").lower() == "unauthorized":
            raise RuntimeError("Given Auth_key for the AmariAPI was invalid. Please head over to your Amari developer dashboard and get a proper authorization token.")

    async def getGuildUser(self, user_id:int, guild_id:int):
        data = await self.url_request(endpoint=f"guild/{guild_id}/member/{user_id}")
        return datamodels.AmariUser(self.bot, data)
    
    async def getGuildLeaderboard(self, guild_id:int, *, page:int=1, limit:int=10):
        data = await self.url_request(endpoint=f"guild/leaderboard/{guild_id}?page={page}&limit={limit}")
        return datamodels.AmariLeaderboard(self.bot, data, guild_id)
        
    async def getLeaderboardPosition(self, user_id:int, guild_id:int):
        leaderboard = await self.getGuildLeaderboard(guild_id, top_count=100)
        if not user_id in leaderboard:
            raise ValueError(f"{user_id} is not present in the leaderboard")
        for index, user in enumerate(leaderboard):
            if user.id == user_id:
                return index, user
            
    async def getWeeklyLeaderboard(self, guild_id:int, *, page:int=1, limit:int=10):
        data = await self.url_request(endpoint=f"guild/weekly/{guild_id}?page={page}&limit={limit}")
        return datamodels.AmariLeaderboard(self.bot, data)

    async def get_or_fetch_member(self, member_id:int):
        if member := self.bot.get_member(member_id):
            return member
        return await self.bot.fetch_member(member_id)
        
    async def url_request(self, *, endpoint=None):
        async with aiohttp.ClientSession(headers={"Authorization": self.auth_key}) as session:
            async with session.get(self.url+endpoint if endpoint else "") as response:
                return await response.json()