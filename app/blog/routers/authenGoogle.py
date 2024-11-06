from fastapi import APIRouter, HTTPException, Request
from authlib.integrations.starlette_client import OAuthError
from fastapi.responses import JSONResponse
from blog.oauth import oauth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/authenGoogle",
    tags=['Google Authen']
)

@router.get("/check-auth")
async def check_auth(request: Request):
    user = request.session.get('user')
    return JSONResponse({
        "isAuthenticated": bool(user),
        "user": user if user else None
    })

@router.get("/login-url")
async def get_login_url(request: Request):
    try:
        redirect_uri = request.url_for('auth')
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Error generating login URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating login URL")

@router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            logger.info(f"Login successful for user: {user.get('email')}")
            logger.info(f"Client IP: {request.client.host}")
            logger.info(f"User Agent: {request.headers.get('user-agent')}")

            # Có thể xem thông tin về client:
            # client_ip = request.client.host
            # user_agent = request.headers.get("user-agent")
            # print(f"Login from: {client_ip}, {user_agent}")


            request.session['user'] = dict(user)
            return JSONResponse({
                "status": "success",
                "user": dict(user),
                "message": "Authentication successful"
            })
        raise HTTPException(status_code=401, detail="Failed to get user info")
    except OAuthError as e:
        logger.error(f"OAuth error: {str(e.error)}")
        return JSONResponse({
            "status": "error",
            "error": str(e.error),
            "message": "Authentication failed"
        }, status_code=401)
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get('/logout')
async def logout(request: Request):
    try:
        # client_ip = request.client.host
        # print(f"Logout from: {client_ip}")
        logger.info(f"Logout request from: {request.client.host}")
        request.session.pop('user', None)
        return JSONResponse({
            "status": "success",
            "message": "Logged out successfully"
        })
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during logout")