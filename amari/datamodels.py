import discord

from dataclasses import dataclass
from redbot.core.bot import Red

class AmariUser:
    """
    A class that represents a AmariBot user with all its attributes.
    
    Some attributes might return None based on the type of request the instance was created from."""
    
    def __init__(self, bot, data={}, guild:discord.Guild=None):
        if data.get("error") and data.get("error").lower() == "user not found":
            raise NameError("The user you requested wasn't found.")
        self.bot : Red = bot
        self.guild : discord.Guild = guild
        self.id : int = data.get("id")
        self.username : str = data.get("username")
        self.experience : int = data.get("exp", 0)
        self.xp = self.experience
        self.level : int = data.get("level", 0)
        self.weeklyxp :int = data.get("weeklyExp", 0) if not len(data) == 3 else data.get("exp", 0)
            
    def __repr__(self) -> str:
        return f"<AmariUser id={self.id} username={self.username} xp={self.xp} level={self.level} weeklyXp={self.weeklyxp} guild={self.guild.__repr__()}>"

    async def getMemberObject(self):
        """Get a proper discord.Member object from your Amariuser instance.

        Returns:
            discord.Member : The proper discord.Member object.
        """
        return await self.get_or_fetch_member(self.id, self.guild)
    
    @staticmethod
    async def get_or_fetch_member(member_id:int, guild:discord.Guild):
        if member := guild.get_member(member_id):
            return member
        try:
            return await guild.fetch_member(member_id)
        except:
            return None
            
class AmariLeaderboard:

    def __init__(self, bot, data={}, guild=None):
        if data:
            self.raw_leaderboard = data.get("data")
            self.total_count = data.get("total_count")
            self.count = data.get("count")
            self.guild = guild
            self.bot = bot
            
    def __repr__(self) -> str:
        return f"<AmariLeaderboard total_count={self.total_count} count={self.count} guild={self.guild.__repr__()}>"
    
    def get_leaderboard(self, count:int=10):
        """
        Method to get a properly formatted leaderboard from the raw one.
        This converts each entry to a `AmariUser` instance."""
        final = []
        if self.raw_leaderboard:
            for index, data in enumerate(self.raw_leaderboard, 1):
                if index <= count:
                    final.append(AmariUser(self.bot, data, self.guild))
                else:
                    break
                
            return final
        else:
            raise ValueError("The leaderboard is empty!")
    
class AmariRewards:
    """
    A class that represents guild level rewards set with AmariBot"""
    def __init__(self, data={}, guild:discord.Guild=None):
        if data:
            self.guild = guild
            self.raw_rewards = data.get("data")
            self.count = data.get("count")
            
    def __repr__(self) -> str:
        return f"<AmariRewards count={self.count} guild={self.guild.__repr__()}>"
            
    async def rewards(self):
        """Get properly formatted guild rewards in a dictionary.
        
        The key is the level number and the value is a discord.Role object obtained from the id provided by the API."""
        final = {}
        if self.raw_rewards:
            for i in self.raw_rewards:
                role = self.guild.get_role(int(i.get("roleID")))
                level = i.get("level")
                final[level] = role
                
            return final
        raise ValueError("This guild has no rewards setup.")