import datetime

from fastapi import Depends

from lib.sql_connect import create_user


class Address:
    city: str = '0'
    street: str = '0'
    house: str = '0'
    latitudes: float = 0  # Широта
    longitudes: float = 0  # Долгота

    def __init__(self, data: dict):
        self.city = data['city']
        self.street = data['street']
        self.house = data['house']
        self.latitudes = data['latitudes']
        self.longitudes = data['longitudes']

    def get_address_json(self) -> dict:
        return {
            'city': self.city,
            'street': self.street,
            'house': self.house,
            'latitudes': self.latitudes,
            'longitudes': self.longitudes,
        }


class Work:
    work_type: str = 'clean',
    object_name: str = '0',
    object_size: int = 0,

    def __init__(self, data: dict):
        self.work_type = data['city']
        self.object_name = data['object_name']
        self.object_size = data['house']

    def get_address_json(self) -> dict:
        return {
            'work_type': self.work_type,
            'object_name': self.object_name,
            'object_size': self.object_size,
        }


class User:
    user_id: int = 0
    name: str = '0'
    phone: int = 0
    email: str = '0'
    auth_type: str = '0'
    auth_id: int = 0
    description: str = '0'
    lang: str = '0'
    range: int = 1
    address: Address = None
    status: str = '0'
    last_active: datetime.datetime = None
    create_date: datetime.datetime = None

    def __init__(self, data: dict = None):
        if data is not None:
            self.user_id = data['user_id']
            self.phone = data['phone']
            self.email = data['email']
            self.name = data['name']
            self.auth_type = data['auth_type']
            self.auth_id = data['auth_id']
            self.description = data['description']
            self.lang = data['lang']
            self.address = Address(data)
            self.status = data['status']
            self.range = data['range']
            self.last_active = data['last_active'] if data['last_active'] != None else None
            self.create_date = data['create_date'] if data['create_date'] != None else None

    def get_user_json(self) -> dict:
        return {
            'user_id': self.user_id,
            'phone': self.phone,
            'email': self.email,
            'name': self.name,
            'auth_type': self.auth_type,
            'auth_id': self.auth_id,
            'description': self.description,
            'lang': self.lang,
            'status': self.status,
            'address': self.address.get_address_json(),
            'last_active': str(self.last_active),
            'create_date': str(self.create_date)
        }

    async def create_user(self, db: Depends):
        self.user_id = (await create_user(db=db, phone=self.phone, email=self.email, name=self.name,
                                         auth_type=self.auth_type, auth_id=self.auth_id, description=self.description,
                                         lang=self.lang, city=self.address.city, street=self.address.street,
                                         house=self.address.house, status=self.status))[0][0]
