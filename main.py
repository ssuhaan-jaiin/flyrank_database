from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from supabase_client import supabase

security_scheme = HTTPBearer()

app = FastAPI(
    title="Auth API",
    version="1.0",
)
print("Connected to Supabase")


class AuthCredentials(BaseModel):
    email: str
    password: str


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")

    token = auth_header.removeprefix("Bearer ").strip()

    if not token:
        raise HTTPException(status_code=401, detail="Access token required")

    try:
        result = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if result is None or result.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"user": result.user, "token": token}


@app.get("/", summary="API info")
def read_root():
    return {"name": "Auth API", "version": "1.0"}


@app.post("/auth/signup", summary="Create a new user account")
def signup(credentials: AuthCredentials):
    if not credentials.email.strip() or not credentials.password.strip():
        return JSONResponse(status_code=400, content={"error": "Email and password are required"})

    try:
        result = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    return JSONResponse(status_code=201, content={"user": result.user.model_dump(mode="json")})


@app.post("/auth/login", summary="Log in and get a JWT")
def login(credentials: AuthCredentials):
    if not credentials.email.strip() or not credentials.password.strip():
        return JSONResponse(status_code=400, content={"error": "Email and password are required"})

    try:
        result = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
    except Exception:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token
    }


@app.post("/auth/logout", summary="Log out")
def logout(current: dict = Depends(get_current_user), _=Depends(security_scheme)):
    supabase.auth.sign_out()
    return JSONResponse(status_code=204, content=None)


@app.get("/public/info", summary="Public info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", summary="Get profile (verified)")
def protected_profile(current: dict = Depends(get_current_user), _=Depends(security_scheme)):
    user = current["user"]
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }


@app.get("/protected/dashboard", summary="Dashboard (verified) — proves the guard is reusable")
def protected_dashboard(current: dict = Depends(get_current_user), _=Depends(security_scheme)):
    user = current["user"]
    return {"message": f"Welcome to your dashboard, {user.email}"}