import logging

from ...client.api_client import api_client
from ...client.models.exceptions import APIException, NotFoundError

from ...client.models.api import Invoice, EnumInvoiceStatus

logger = logging.getLogger("scripts.startup.invoices")

async def invoices_sync(invoice_ids: list[int]) -> dict[int, Invoice]:
    max_count = len(invoice_ids)
    output = {}

    logger.info("Invoices to load: %s", max_count)
    
    for i, invoice_id in enumerate(invoice_ids):
        try:
            invoice = await api_client.check_invoice(invoice_id=invoice_id)
            invoice_model = Invoice(**invoice)

            if invoice_model.status == EnumInvoiceStatus.PENDING:
                user = await api_client.get_user_by_id(user_id=invoice_model.user_id)
                
                logger.debug("[%s/%s] Load invoice: %s",
                             i, max_count,
                             invoice_id)
                
                output[user.telegram_id] = invoice
            
            else:
                logger.debug("Skip invoice, status: %s", invoice_model.status)

        except NotFoundError:
            logger.warning("NotFoundError while load invoice: %s",
                           invoice_id)

        except APIException as exc:
            logger.warning("APIException while load invoice: %s | Exception: %s",
                           invoice_id,
                           exc.args)

        except Exception as exc:
            logger.exception("Unexpected exception",
                             exc_info=True)

    logger.info("Loaded invoices: [%s / %s]", len(output), max_count)

    return output