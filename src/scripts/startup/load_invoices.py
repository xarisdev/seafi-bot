import logging

from ...client.api_client import api_client
from ...client.models.exceptions import APIException, NotFoundError

from ...client.models.api import Invoice, EnumInvoiceStatus

logger = logging.getLogger("scripts.startup.invoices")

async def invoices_sync(invoices: dict[int, dict]) -> dict[int, Invoice]:
    count = 0
    max_count = len(invoices)
    
    output = {}

    for telegram_id, invoice_data in invoices.items():
        invoice_id = invoice_data.get("id")

        count += 1

        try:
            invoice = await api_client.check_invoice(invoice_id=invoice_id)

            if invoice.status == EnumInvoiceStatus.PENDING:
                logger.debug("[%s/%s] Load invoice: %s",
                             count, max_count,
                             invoice_id)
                
                output[telegram_id] = invoice
            
            else:
                logger.debug("Skip invoice, status: %s", invoice.status)

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