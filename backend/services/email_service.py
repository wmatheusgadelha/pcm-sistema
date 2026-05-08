from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings

def _send_email(to: List[str], subject: str, html_body: str):
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print(f"[EMAIL] Simulado para {to}: {subject}")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        msg["To"] = ", ".join(to)
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to, msg.as_string())
        print(f"[EMAIL] Enviado para {to}: {subject}")
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar: {e}")

def send_preventiva_alert(emails: List[str], equipamento: str, tipo: str, data_prevista: str, responsavel: str):
    subject = f"⚠️ Manutenção Programada: {equipamento} — {data_prevista}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:8px;">
      <div style="background:#0f1923;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:#38bdf8;margin:0;font-size:20px;">⚙ PCM — Alerta de Manutenção</h2>
      </div>
      <div style="background:#fff;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e5e7eb;">
        <p style="color:#374151;font-size:15px;">Olá, <strong>{responsavel}</strong>!</p>
        <p style="color:#374151;">Uma manutenção programada está se aproximando do vencimento:</p>
        <div style="background:#f0f9ff;border-left:4px solid #38bdf8;padding:16px;border-radius:4px;margin:16px 0;">
          <p style="margin:4px 0;color:#0f1923;"><strong>Equipamento:</strong> {equipamento}</p>
          <p style="margin:4px 0;color:#0f1923;"><strong>Tipo:</strong> {tipo}</p>
          <p style="margin:4px 0;color:#dc2626;"><strong>Data prevista:</strong> {data_prevista}</p>
        </div>
        <p style="color:#6b7280;font-size:13px;">Acesse o sistema PCM para criar a Ordem de Serviço e registrar a execução.</p>
        <p style="color:#9ca3af;font-size:12px;margin-top:24px;">— {settings.APP_NAME}</p>
      </div>
    </div>
    """
    _send_email(emails, subject, html)

def send_os_created(emails: List[str], numero_os: str, equipamento: str, tipo: str, responsavel: str, descricao: str):
    subject = f"Nova OS #{numero_os} — {tipo} em {equipamento}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:8px;">
      <div style="background:#0f1923;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:#38bdf8;margin:0;font-size:20px;">⚙ PCM — Nova Ordem de Serviço</h2>
      </div>
      <div style="background:#fff;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e5e7eb;">
        <p style="color:#374151;">Uma nova OS foi aberta e atribuída a <strong>{responsavel}</strong>:</p>
        <div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:16px;border-radius:4px;margin:16px 0;">
          <p style="margin:4px 0;"><strong>OS:</strong> #{numero_os}</p>
          <p style="margin:4px 0;"><strong>Equipamento:</strong> {equipamento}</p>
          <p style="margin:4px 0;"><strong>Tipo:</strong> {tipo}</p>
          <p style="margin:4px 0;"><strong>Descrição:</strong> {descricao}</p>
        </div>
        <p style="color:#9ca3af;font-size:12px;margin-top:24px;">— {settings.APP_NAME}</p>
      </div>
    </div>
    """
    _send_email(emails, subject, html)

def send_welcome_email(email: str, nome: str, senha_temporaria: Optional[str] = None):
    subject = f"Bem-vindo ao {settings.APP_NAME}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:8px;">
      <div style="background:#0f1923;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:#38bdf8;margin:0;">⚙ PCM — Acesso Liberado</h2>
      </div>
      <div style="background:#fff;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e5e7eb;">
        <p>Olá, <strong>{nome}</strong>! Seu acesso ao sistema PCM foi criado.</p>
        <p><strong>Login:</strong> {email}</p>
        {"<p><strong>Senha temporária:</strong> " + senha_temporaria + "</p>" if senha_temporaria else ""}
        <p style="color:#9ca3af;font-size:12px;margin-top:24px;">— {settings.APP_NAME}</p>
      </div>
    </div>
    """
    _send_email([email], subject, html)
