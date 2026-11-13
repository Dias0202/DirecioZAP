from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_FROM: str
    VERIFY_TOKEN: str
    # Public URL configured in the Twilio console for the webhook, e.g.
    # https://abc123.ngrok-free.app/webhook. Optional: when empty, the URL is
    # rebuilt from the proxy's X-Forwarded-* headers.
    TWILIO_WEBHOOK_URL: str = ""
    SUPABASE_URL: str
    SUPABASE_KEY: str
    EXCEL_PATH: str = "./data/fornecedores.xlsx"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
