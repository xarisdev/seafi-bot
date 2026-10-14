from .info import (
    bot_info_handler
)
from .menu import (
    menu_handler
)
from .payment import (
    payment_check_handler,
    payment_cancel_handler
)
from .plans import (
    plans_list_handler,
    plans_setup_handler,
    selected_plan_info_handler,
    select_payment_methods_handler,
    selected_payment_method_handler
)

from .commands.start import start_command_handler
from .commands.info import bot_info_command_handler

from .conversations.plan_create import conversation as plan_create_conversation
from .conversations.plan_patch import conversation as plan_patch_conversation

from .verify_user import verify_handler

handlers = {
    -2: [start_command_handler, bot_info_command_handler],
    -1: [verify_handler],
    1: [
        plan_create_conversation,
        plan_patch_conversation,

        menu_handler,
        bot_info_handler,
        
        plans_list_handler,
        plans_setup_handler,
        selected_plan_info_handler,
        select_payment_methods_handler,
        selected_payment_method_handler,
        
        payment_check_handler,
        payment_cancel_handler
    ]
}