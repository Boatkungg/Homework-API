from typing import Optional

from databases import Database


class DB:
    def __init__(self, db_path: str, force_rollback: bool = False):
        self.database = Database(db_path, force_rollback=force_rollback)
        self.connected = False

    async def connect(self):
        assert not self.connected, "database should be connect first via .connect()"

        await self.database.connect()
        self.connected = True

    async def disconnect(self):
        assert self.connected, "database should be connect first via .connect()"

        await self.database.disconnect()
        self.connected = False

    async def execute(self, query, values: Optional[dict] = None):
        assert self.connected, "database should be connect first via .connect()"

        return await self.database.execute(query=query, values=values)

    async def fetch_one(self, query, values: Optional[dict] = None):
        assert self.connected, "database should be connect first via .connect()"

        return await self.database.fetch_one(query=query, values=values)

    async def fetch_all(self, query, values: Optional[dict] = None):
        assert self.connected, "database should be connect first via .connect()"

        return await self.database.fetch_all(query=query, values=values)
