from aiogram import Router, Bot

from bot.models.resume_handler import ResumeHandler


def setup_handlers(router: Router, bot: Bot):
    ResumeHandler(router, bot)

