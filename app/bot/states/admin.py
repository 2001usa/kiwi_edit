from aiogram.fsm.state import State, StatesGroup

class AddMediaStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_type = State()
    waiting_for_genre = State()
    waiting_for_confirmation = State()

class AddEpisodeStates(StatesGroup):
    waiting_for_media_code = State()
    waiting_for_file = State()
    waiting_for_episode_number = State()

class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()

class SponsorshipStates(StatesGroup):
    menu = State()
    waiting_for_channel_id = State()
    waiting_for_channel_name = State()
    waiting_for_channel_link = State()
    waiting_for_user_limit = State()

class StaffStates(StatesGroup):
    menu = State()
    waiting_for_id = State()

class PostingStates(StatesGroup):
    search = State()
    waiting_for_confirmation = State()
