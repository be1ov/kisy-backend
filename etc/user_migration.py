import csv
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.modules.users.entities import UserEntity
from app.core.db.session import get_session


async def parse_and_insert_users(db: AsyncSession = Depends(get_session)):
    users_to_add: List[UserEntity] = []

    print('start4')
    with open('etc/users.csv', mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)

        print('start5')
        for row in reader:
            user = UserEntity(
                telegram_id=int(row['user_id']),
                first_name=row['name'],
                phone=row['phone_number'],
            )
            print(user)
            users_to_add.append(user)

    db.add_all(users_to_add)
    await db.commit()

    return {"message": f"Successfully added {len(users_to_add)} users"}


if __name__ == "__main__":
    import asyncio
    print('start')
    from app.core.db.session import engine


    async def main():
        print('start2')
        async with engine.begin() as conn:
            print('start3')
            async with AsyncSession(engine) as session:
                await parse_and_insert_users(session)


    asyncio.run(main())