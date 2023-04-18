import aiohttp

async def user_fb_check_auth(access_token: str, user_id: int, email: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://graph.facebook.com/{user_id}?fields=id,name,email&access_token={access_token}', ssl=False) as resp:
            answer = await resp.json()
            print(answer)
            if resp.status != 200:
                return False

            if answer['email'] == email:
                return True

            return False
