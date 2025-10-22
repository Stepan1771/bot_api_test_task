import logging
import os
from io import BytesIO

from PyPDF2 import PdfReader
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.filters import StateFilter
from typing import Optional, Dict

from docx import Document


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCommandHandler:

    COMMANDS: Dict[str, str] = {}

    STATE_FILTERS: Dict[str, Optional[State]] = {}


    def __init__(self, router: Router, bot: Bot):
        self.bot = bot
        self.router = router
        self._register_handlers()


    def _register_handlers(self):
        for command, handler_name in self.COMMANDS.items():
            handler = getattr(self, handler_name)

            state_filter = self.STATE_FILTERS.get(handler_name)

            if state_filter is not None:
                self.router.message(
                    F.text == command,
                    StateFilter(state_filter)
                )(handler)
            else:

                self.router.message(F.text == command)(handler)

        for handler_name, state in self.STATE_FILTERS.items():
            if handler_name not in self.COMMANDS.values():
                handler = getattr(self, handler_name)
                self.router.message(StateFilter(state))(handler)


    @staticmethod
    async def send_answer(
            message: Message,
            text: str,
            reply_markup=None
    ):

        await message.answer(text, reply_markup=reply_markup)


    @staticmethod
    def parse_pdf(file_bytes: BytesIO):
        reader = PdfReader(file_bytes)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text


    @staticmethod
    def parse_docx(file_bytes: BytesIO):
        document = Document(file_bytes)
        full_text = ""
        for paragraph in document.paragraphs:
            full_text += paragraph.text + "\n"
        return full_text


    async def parse_file(
            self,
            message: Message,
            state: FSMContext,
    ):
        if not message.document:
            await self.send_answer(
                message=message,
                text="Пожалуйста, отправьте файл!",
                reply_markup=None,
            )
            return

        input_file = message.document
        filename = input_file.file_name

        logger.info(f"Получен файл: {filename}")

        try:
            file_info = await self.bot.get_file(input_file.file_id)
            logger.info(f"Информация о файле получена: {file_info.file_path}")

            downloads_dir = 'downloads'
            os.makedirs(downloads_dir, exist_ok=True)
            save_path = os.path.join(downloads_dir, filename)
            logger.info(f"Планируем сохранить файл по пути: {save_path}")

            file_bytes = await self.bot.download_file(file_info.file_path)
            if file_bytes is None:
                logger.warning("Файл не был скачан.")
            else:
                if isinstance(file_bytes, BytesIO):
                    size = len(file_bytes.getvalue())
                    logger.info(f"Файл {filename} успешно скачан, размер: {size} байт")
                else:
                    logger.warning("Неизвестный тип объекта файла")

                with open(save_path, 'wb') as new_file:
                    new_file.write(file_bytes.getvalue())
                logger.info(f"Файл сохранен по пути: {save_path}")

                ext = os.path.splitext(filename)[1].lower()

                if ext == '.pdf':
                    text_content = self.parse_pdf(file_bytes)
                elif ext == '.docx':
                    text_content = self.parse_docx(file_bytes)
                else:
                    text_content = "Парсинг данного типа файла не поддерживается."

                await self.send_answer(
                    message=message,
                    text=f"Содержимое файла:\n{text_content}",
                    reply_markup=None,
                )

                await state.clear()

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {str(e)}")
            await self.send_answer(
                message=message,
                text=f"Ошибка при сохранении файла: {str(e)}",
                reply_markup=None,
            )