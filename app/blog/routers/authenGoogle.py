from fastapi import APIRouter, Depends, Request, status, HTTPException
from typing import Optional
from authlib.integrations.starlette_client import OAuthError
from fastapi.responses import JSONResponse
from blog.oauth import oauth
import logging
import random
import string
import os
from dotenv import load_dotenv

from sqlalchemy.orm import Session
from blog.database import get_db
from blog.repository import user as user_repo
from blog.repository import userInfo as user_info_repo
from blog.token import create_access_token
from blog.hashing import Hash
import secrets
from blog import schemas

load_dotenv()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'development':
    REDIRECT_URI = 'http://localhost:8000/authenGoogle/auth'
    BASE_URL = 'http://localhost:8000'
else:
    REDIRECT_URI = 'https://pbl6-travel-fastapi-azfpceg2czdybuh3.eastasia-01.azurewebsites.net/authenGoogle/auth'
    BASE_URL = 'https://pbl6-travel-fastapi-azfpceg2czdybuh3.eastasia-01.azurewebsites.net'


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/authenGoogle",
    tags=['Google Authen']
)


@router.get("/login-url")
async def get_login_url(request: Request):
    try:
        # Sử dụng BASE_URL để xây dựng URL đầy đủ
        redirect_uri = f"{BASE_URL}/authenGoogle/auth"
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Error in login-url: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        # print("this is token:  ")
        # for key in token:
        #     print(key, token[key])
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user info"
            )

        email = user_info.get('email')
        # print("email", email)
        existing_user = user_repo.get_user_by_email(email, db)
        
        if existing_user:
            logger.info(f"Existing user logged in: {email}")
            access_token = create_access_token(
                data={"email": existing_user.email, "role": existing_user.role}
            )
        else:
            try:
                new_user = schemas.User(
                    username=user_info.get('name', ''),
                    email=email,
                    password=Hash.hash_password(secrets.token_urlsafe(32)),
                    role="guest",
                    status="enable"
                )
                
                created_user = user_repo.create(new_user, db)
                if not created_user:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create new user"
                    )
                
                try:
                    user_info_data = schemas.UserInfoBase(
                        description="",
                        phone_number="0"
                    )
                    
                    address_data = schemas.Address(
                        district="",
                        street="",
                        ward="",
                        city_id=1
                    )
                    
                    user_info_result = user_info_repo.create_user_info_by_userid(
                        user_info_data,
                        address_data,
                        created_user.id,
                        db
                    )
                    
                    if not user_info_result:
                        db.rollback()
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to create user information"
                        )

                    # Thêm avatar mặc định
                    try:
                        await user_info_repo.add_default_avatar(db, user_info_result.id)
                    except Exception as avatar_error:
                        logger.error(f"Error adding default avatar: {str(avatar_error)}")
                        # Không rollback toàn bộ nếu thêm avatar thất bại
                        # Có thể xử lý riêng tùy theo yêu cầu
                    
                except Exception as user_info_error:
                    db.rollback()
                    logger.error(f"Error creating user info: {str(user_info_error)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create user information: {str(user_info_error)}"
                    )
                
                logger.info(f"New user created: {email}")
                access_token = create_access_token(
                    data={"email": created_user.email, "role": created_user.role}
                )
                
            except HTTPException as he:
                raise he
            except Exception as create_user_error:
                logger.error(f"Error creating user: {str(create_user_error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user: {str(create_user_error)}"
                )

        return JSONResponse({
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer"
        })
        
    except OAuthError as e:
        logger.error(f"OAuth error: {str(e.error)}")
        return JSONResponse({
            "status": "error",
            "error": str(e.error),
            "message": "Authentication failed"
        }, status_code=status.HTTP_401_UNAUTHORIZED)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
# @router.get('/logout')
# async def logout(request: Request):
#     try:
#         # client_ip = request.client.host
#         # print(f"Logout from: {client_ip}")
#         logger.info(f"Logout request from: {request.client.host}")
#         request.session.pop('user', None)
#         return JSONResponse({
#             "status": "success",
#             "message": "Logged out successfully"
#         })
#     except Exception as e:
#         logger.error(f"Error during logout: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error during logout")
    
# @router.get("/check-auth")
# async def check_auth(request: Request):
#     user = request.session.get('user')
#     return JSONResponse({
#         "isAuthenticated": bool(user),
#         "user": user if user else None
#     })

# @router.get('/auth')
# async def auth(request: Request):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#         user = token.get('userinfo')
#         if user:
#             logger.info(f"Login successful for user: {user.get('email')}")
#             logger.info(f"Client IP: {request.client.host}")
#             logger.info(f"User Agent: {request.headers.get('user-agent')}")

#             # Có thể xem thông tin về client:
#             # client_ip = request.client.host
#             # user_agent = request.headers.get("user-agent")
#             # print(f"Login from: {client_ip}, {user_agent}")


#             request.session['user'] = dict(user)
#             return JSONResponse({
#                 "status": "success",
#                 "user": dict(user),
#                 "message": "Authentication successful"
#             })
#         raise HTTPException(status_code=401, detail="Failed to get user info")
#     except OAuthError as e:
#         logger.error(f"OAuth error: {str(e.error)}")
#         return JSONResponse({
#             "status": "error",
#             "error": str(e.error),
#             "message": "Authentication failed"
#         }, status_code=401)
#     except Exception as e:
#         logger.error(f"Unexpected error during authentication: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")
