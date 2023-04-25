get_me_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user_id': 12,
                                  'name': 'Anna',
                                  'surname': 'Volkova',
                                  'phone': 321161666,
                                  'email': 'anna@gmail.com',
                                  'status': 'creator',
                                  'last_active': '2023-01-17 21:54:23.738397',
                                  }
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": 'bad access token'
                    },
                }
            }
        }
    },
}

access_token_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user_id': 12,
                                  'access_token': 'fFsok0mod3y5mgoe203odk3f'}
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": 'bad refresh token, please login'
                    },
                }
            }
        }
    },
}

check_phone_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True, 'desc': 'no phone in database'}
                    },
                }
            }
        }
    },
    226: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": 'have user with same phone'
                    },
                }
            }
        }
    },
}

create_user_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user_id': 1,
                                  'access_token': '123',
                                  'refresh_token': '123'}
                    },
                }
            }
        }
    },
}

update_user_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'desc': 'all users information updated'}
                    },
                }
            }
        }
    },
}

update_user_status_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'desc': 'users status updated'}
                    },
                }
            }
        }
    },
}

update_user_profession_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'description': 'users work list updated'}
                    },
                }
            }
        }
    },
}

login_get_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'desc': 'all users information updated'}
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'Bad auth_id or access_token'}
                    },
                }
            }
        }
    },
}

update_pass_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'desc': 'all users information updated'}
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": "bad phone or password"
                    },
                }
            }
        }
    },
}

upload_files_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value":
                            {'ok': True,
                             'creator_id': 3,
                             'file_name': '12.jpg',
                             'file_type': 'image',
                             'file_id': 12,
                             'url': f"http://127.0.0.1:80/file_download?file_id=12"}
                    }
                },
            }
        }
    }
}

upload_files_list_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value":
                            {'ok': True,
                             'desc': "all file list by file line",
                             'files': [{
                                 'file_id': 22,
                                 'name': '12.jpg',
                                 'file_type': 'image',
                                 'owner_id': 12,
                                 'create_date': '2023-01-17 21:54:23.738397',
                                 'url': f"http://127.0.0.1:80/file_download?file_id=12"
                             }]}
                    }
                },
            }
        }
    }
}

get_object_list_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'object_types': [{
                                      "id": 1,
                                      "name_ru": "Квартира",
                                      "name_en": "Apartment",
                                      "name_heb": "דִירָה"
                                  }]
                                  }
                    },
                }
            }
        }
    },
}

update_push_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {'ok': True, 'desc': 'successfully updated'}
                    },
                }
            }
        }
    },
}

send_push_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {'ok': True, 'desc': 'successful send push'}
                    },
                }
            }
        }
    },
}

new_msg_created_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True, 'desc': 'New message was created successfully.'}
                    },
                }
            }
        }
    },
}

get_msg_list_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {
                            "ok": True,
                            "count": 1,
                            "msg_list": [
                                {
                                    "id": 1,
                                    "msg_id": 0,
                                    "msg_type": "text",
                                    "title": "Test Title",
                                    "text": "text",
                                    "description": "0",
                                    "lang": "en",
                                    "from_user": 2,
                                    "to_user": 2,
                                    "status": "created",
                                    "user_type": "user",
                                    "read_date": "None",
                                    "deleted_date": "None",
                                    "create_date": "2023-04-24 11:17:13.655705"
                                }
                            ]
                        }
                    },
                }
            }
        }
    },
}

get_msg_by_id_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {
                            "ok": True,
                            "message": {
                                "id": 1,
                                "msg_id": 0,
                                "msg_type": "text",
                                "title": "Test Title",
                                "text": "text",
                                "description": "0",
                                "lang": "en",
                                "from_user": {
                                    "user_id": 2,
                                    "phone": 37529821,
                                    "email": "windownik@gmail.com",
                                    "image_link": "https://platform-lookaside.fbsbx.com/platform/profilepic/?asid=6116895105070527&width=200&ext=1684829559&hash=AeQ4MUkYJgAP4GeFRx8",
                                    "name": "Никита Мисливец",
                                    "auth_type": "fb",
                                    "auth_id": 6116895105070527,
                                    "description": "Nothing about me\n",
                                    "lang": "en",
                                    "status": "admin",
                                    "score": 5,
                                    "score_count": 0,
                                    "total_score": 0,
                                    "address": {
                                        "city": "Paris",
                                        "street": "San Marino ",
                                        "house": "1",
                                        "latitudes": 53.6878483,
                                        "longitudes": 53.6878483
                                    },
                                    "last_active": "2023-04-23 13:29:29.788615",
                                    "create_date": "2023-04-23 12:30:39.470459"
                                },
                                "to_user": {
                                    "user_id": 2,
                                    "phone": 37529821,
                                    "email": "windownik@gmail.com",
                                    "image_link": "https://platform-lookaside.fbsbx.com/platform/profilepic/?asid=6116895105070527&width=200&ext=1684829559&hash=AeQ4MUkYJgAP4GeFRx8",
                                    "name": "Никита Мисливец",
                                    "auth_type": "fb",
                                    "auth_id": 6116895105070527,
                                    "description": "Nothing about me\n",
                                    "lang": "en",
                                    "status": "admin",
                                    "score": 5,
                                    "score_count": 0,
                                    "total_score": 0,
                                    "address": {
                                        "city": "Paris",
                                        "street": "San Marino ",
                                        "house": "1",
                                        "latitudes": 53.6878483,
                                        "longitudes": 53.6878483
                                    },
                                    "last_active": "2023-04-23 13:29:29.788615",
                                    "create_date": "2023-04-23 12:30:39.470459"
                                },
                                "status": "created",
                                "user_type": "user",
                                "read_date": "None",
                                "deleted_date": "None",
                                "create_date": "2023-04-24 11:17:13.655705"
                            }
                        }
                    },
                }
            }
        }
    },
}
