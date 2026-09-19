from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase_client import supabase

app = FastAPI()
print("Connected to Supabase")


class AuthCredentials(BaseModel):
    email: str
    password: str


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