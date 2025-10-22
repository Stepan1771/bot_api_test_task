from aiogram.fsm.state import StatesGroup, State


class UploadFileFSM(StatesGroup):
    download_file = State()
