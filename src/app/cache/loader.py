from typing import Any

from .filters import filters

from ...scripts.startup.load_invoices import invoices_sync
from ...scripts.startup.load_subscriptions import subscriptions_sync

async def serialize_data(data: dict[str, Any]) -> dict[str, Any]:
    output = {}

    for filter in filters:
        
        # ------------ Serializing ------------

        key = filter.input_data_key
        values = data.get(filter.output_data_key)

        if values is None:
            continue

        serialized_data = filter.deserialize(data=values)

        # ------------ API check ------------
        
        if key == "pending_invoices":
            result = await invoices_sync(serialized_data)

        elif key == "subscriptions":
            result = await subscriptions_sync(serialized_data)

        else: # Локальные данные
            result = serialized_data
        
        # ------------ Writing result ------------

        output[key] = result

    return output