import aiohttp

async def user_fb_check_auth(access_token: str, user_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://graph.facebook.com/{user_id}?access_token={access_token}', ssl=False) as resp:

            if resp.status == 200:
                return True
            return False