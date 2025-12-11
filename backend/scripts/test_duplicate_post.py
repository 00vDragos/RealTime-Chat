import asyncio
import requests
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.users import User
from app.core.security import create_access_token
from datetime import timedelta


async def make_token(email: str):
	async with AsyncSessionLocal() as db:
		res = await db.execute(select(User).where(User.email == email))
		user = res.scalars().first()
		if not user:
			raise SystemExit('user not found')
		data = {"id": str(user.id), "email": user.email}
		token = create_access_token(data=data, expires_delta=timedelta(minutes=60))
		return token


def do_post(token: str):
	url = 'http://localhost:8000/api/messages/new_conversation'
	headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
	data = {'participant_ids': ['6a0bc187-2f37-44c2-8adb-747783188f8c', 'c4ba3f58-9da0-4a84-bb46-1fd51ed530af', 'ec20442f-8df4-470f-8897-5b1a03c65e5a']}
	resp = requests.post(url, json=data, headers=headers)
	print(resp.status_code)
	print(resp.text)


if __name__ == '__main__':
	token = asyncio.run(make_token('alice@example.com'))
	do_post(token)
