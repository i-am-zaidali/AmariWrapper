import discord

class AmariUser:
    """
    A class that represents a AmariBot user with all its attributes.
    
    Some attributes might return None based on the type of request the instance was created from."""
    def __init__(self, bot, data={}, guild:discord.Guild=None):
        if data.get("error") and data.get("error").lower() == "user not found":
            raise NameError("The user you requested wasn't found.")
        self.bot = bot
        self.guild = guild
        self.id = data.get("id")
        self.username = data.get("username")
        self.experience = data.get("exp")
        self.xp = self.experience
        self.level = data.get("level")
        self.weeklyxp = data.get("weeklyExp") if not len(data) == 3 else data.get("exp")
            
    def __repr__(self) -> str:
        return f"<AmariUser id={self.id} username={self.username} xp={self.xp} level={self.level} weeklyXp={self.weeklyxp} guild={self.guild.__repr__()}>"

    async def getMemberObject(self):
        return await self.get_or_fetch_member(self.bot, self.id)
    
    @staticmethod
    async def get_or_fetch_member(bot, member_id:int):
        if member := bot.get_member(member_id):
            return member
        return await bot.fetch_member(member_id)
            
class AmariLeaderboard:
    """
    A class that represents an AmariBot guild leaderboard.
    """
    def __init__(self, bot, data={}, guild=None):
        if data:
            self.raw_leaderboard = data.get("data")
            self.total_count = data.get("top_count")
            self.count = data.get("count")
            self.guild = guild
            self.bot = bot
            
    def __repr__(self) -> str:
        return f"<AmariLeaderboard total_count={self.total_count} count={self.count} guild={self.guild.__repr__()}>"
            
    def get_leaderboard(self, count:int=10):
        final = []
        if self.raw_leaderboard:
            for index, data in enumerate(self.raw_leaderboard, 1):
                if index < count:
                    final.append(AmariUser(data))
                else:
                    break
                
            return final
        else:
            raise ValueError("The leaderboard is empty!")
        
    def __iter__(self):
        return self.get_leaderboard(100)
    
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
        final = {}
        if self.raw_rewards:
            for i in self.raw_rewards:
                role = self.guild.get_role(i.get("roleId"))
                level = i.get("level")
                final[level] = role
                
            return final
        raise ValueError("This guild has no rewards setup.")