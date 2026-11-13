import hmac
import os

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, Response

from config import settings
from conversation import ConversationManager
from twilio_signature import is_valid_signature
from whatsapp import send_message

app = FastAPI(title="DirecioZap Bot")
manager = ConversationManager()


@app.get("/")
def health():
    return {"status": "ok"}


def _public_url(request: Request) -> str:
    """URL that Twilio called, which is the URL it signed.

    Behind ngrok or Render the app sees an internal URL, so the public one is
    taken from TWILIO_WEBHOOK_URL when set, otherwise rebuilt from the
    X-Forwarded-Proto / X-Forwarded-Host headers set by the proxy.
    """
    if settings.TWILIO_WEBHOOK_URL:
        return settings.TWILIO_WEBHOOK_URL
    proto = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    url = f"{proto}://{host.split(',')[0].strip()}{request.url.path}"
    if request.url.query:
        url += f"?{request.url.query}"
    return url


@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()

    signature = request.headers.get("x-twilio-signature")
    if not is_valid_signature(
        _public_url(request), form.multi_items(), signature, settings.TWILIO_AUTH_TOKEN
    ):
        raise HTTPException(status_code=403, detail="Assinatura do Twilio inválida")

    num_media = int(form.get("NumMedia", "0"))
    phone = form.get("From", "").replace("whatsapp:", "").lstrip("+")
    text = form.get("Body", "").strip()

    if not phone:
        return Response(status_code=200)

    if num_media > 0:
        send_message(phone, "Por favor, responda apenas com texto.")
        return Response(status_code=200)

    if not text:
        return Response(status_code=200)

    response = manager.process(phone, text)
    send_message(phone, response)

    return Response(status_code=200)


@app.get("/exportar")
def exportar(x_verify_token: str | None = Header(default=None)):
    # The token travels in a header, not in the query string, so it does not end
    # up in proxy, ngrok or Render access logs.
    if not x_verify_token or not hmac.compare_digest(x_verify_token, settings.VERIFY_TOKEN):
        raise HTTPException(status_code=403, detail="Token inválido")
    path = settings.EXCEL_PATH
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Nenhum cadastro salvo ainda")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="fornecedores.xlsx",
    )
