import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ["https://jcioihlxtitzmgevompq.supabase.co"]
SUPABASE_KEY = os.environ["sb_publishable_QH0EHUIxS7yKRwSPT4crLw_mYP82BXV"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)