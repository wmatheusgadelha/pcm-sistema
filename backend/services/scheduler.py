from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models.user import PlanoPreventiva, User
from .email_service import send_preventiva_alert

scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

def check_preventivas_vencendo():
    db: Session = SessionLocal()
    try:
        hoje = datetime.now()
        limite = hoje + timedelta(days=3)
        planos = db.query(PlanoPreventiva).filter(
            PlanoPreventiva.is_active == True,
            PlanoPreventiva.proxima_execucao <= limite,
            PlanoPreventiva.proxima_execucao >= hoje
        ).all()
        for plano in planos:
            emails = []
            if plano.responsavel_rel and plano.responsavel_rel.email:
                emails.append(plano.responsavel_rel.email)
            admins = db.query(User).filter(User.role.in_(["admin", "gestor"]), User.is_active == True).all()
            for admin in admins:
                if admin.email not in emails:
                    emails.append(admin.email)
            if emails:
                equip_nome = plano.equipamento_rel.nome if plano.equipamento_rel else "Equipamento"
                resp_nome = plano.responsavel_rel.nome if plano.responsavel_rel else "Responsável"
                data_str = plano.proxima_execucao.strftime("%d/%m/%Y")
                send_preventiva_alert(emails, equip_nome, plano.tipo, data_str, resp_nome)
                print(f"[SCHEDULER] Alerta enviado para {emails} — {equip_nome}")
    except Exception as e:
        print(f"[SCHEDULER] Erro: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(
        check_preventivas_vencendo,
        CronTrigger(hour=7, minute=0),
        id="check_preventivas",
        replace_existing=True
    )
    scheduler.start()
    print("[SCHEDULER] Agendador iniciado — verificação diária às 07:00")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
