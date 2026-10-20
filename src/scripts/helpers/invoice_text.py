def _invoice_pending_text() -> str:
    return (f"⏳ <b>Ожидание платежа..</b>")

def _invoice_completed_text() -> str:
    return (f"✅ <b>Успешная оплата!</b>")

def _invoice_cancelled_text() -> str:
    return (f"⛔️ <b>Платеж был отменен</b>\n\n"
            f"<i>❗️Если вы не отменяли платеж, попробуйте еще раз позднее</i>")

def _invoice_failed_text() -> str:
    return (f"⛔️ <b>Ошибка платежа</b>\n\n"
            f"<i>❗️Попробуйте еще раз позднее</i>")

MESSAGES_TEMPLATE = {
    "pending": _invoice_pending_text,
    "completed": _invoice_completed_text,
    "cancelled": _invoice_cancelled_text,
    "failed": _invoice_failed_text
}