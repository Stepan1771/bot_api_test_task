import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.fsm.fsm_states import UploadFileFSM
from bot.models.base_command_handler import BaseCommandHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeHandler(BaseCommandHandler):
    COMMANDS = {
        "/resume": "cmd_resume_handle_request",
    }

    STATE_FILTERS = {
        "cmd_resume_handle_response": UploadFileFSM.download_file,
    }

    async def cmd_resume_handle_request(self, message: Message, state: FSMContext):
        await state.set_state(UploadFileFSM.download_file)
        await self.send_answer(
            message=message,
            text="Оправьте резюме в формате PDF или DOCX",
            reply_markup=None,
        )

    async def cmd_resume_handle_response(self, message: Message, state: FSMContext):
        await self.parse_file(message=message, state=state)








