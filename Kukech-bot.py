from aiogram import Bot, Dispatcher as dp, types, executor, filters, utils
import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import DB_Manipulations as DB
import re

bot = Bot(config.TOKEN)
dp = dp(bot, storage=MemoryStorage())
AUDIO_ID = ''

class States(StatesGroup):
    BASIC_STATE = State()
    SET_FILE = State()
    SET_NAME = State()




@dp.message_handler(commands=["Help"], state=[States.BASIC_STATE])
async def send_help(message:types.Message):
    await message.reply("Используйте команду /Add чтобы добавить новый аудио файл, команду /Cancel чтобы отменить процесс добавления команду /Audios чтобы посмотреть список всех аудиофайлов "
                        "команду /Delete name (например /Delete audio_2) чтобы удалить файл из базы и команду /Voice (например /Voice audio_1) чтобы бот отправил вам этот аудио файл"
                        "Используйте команду /Rename old name --set_new new name чтобы переименовать файл ")



@dp.message_handler(filters.CommandStart())
async def send_start_information(message:types.Message):
    #await bot.promote_chat_member('-1001423174338', '388142124', can_delete_messages=True, can_pin_messages=True, can_change_info=True, can_promote_members=True, can_restrict_members=True, can_invite_users=True)
    #await change_title()
    await States.BASIC_STATE.set()
    await message.reply("Этот бот создан для защиты человечевства от кукечей, для подробной информации воспользуйтесь командой /Help")

@dp.message_handler(state=[States.BASIC_STATE], commands=["Add"])
async def prepeare_to_add(message:types.Message):
    await message.reply("Теперь отправьте аудиофайл который вы хотите добавить в базу данных")
    await States.SET_FILE.set()

@dp.message_handler(state=[States.SET_FILE], content_types=[types.ContentType.AUDIO, types.ContentType.VOICE])
async def receive_audio(message:types.Message, state:FSMContext):
    try:
        id = message.audio.file_id
    except AttributeError:
        id = message.voice.file_id
    exist = await DB.check_if_exist(id, column_name='file_id')
    if not exist:
        globals()["AUDIO_ID"] = id
        await state.set_state(States.SET_NAME)
        await message.reply("Теперь отправьте имя которое вы хотите присвоить этому файлу")
    else:
        await state.set_state(States.BASIC_STATE)
        await message.reply("В базе уже есть такой файл ")

@dp.message_handler(state=[States.SET_NAME])
async def set_audio_name(message: types.Message, state: FSMContext):
    FILE_ID = globals()["AUDIO_ID"]
    name = message.text.strip()
    await DB.add(columns=['name', 'file_id'], values=[name, FILE_ID])
    globals()["AUDIO_ID"] = ''
    await state.set_state(States.BASIC_STATE)
    await message.reply("Аудиофайл {} успешно добавлен".format(name))



@dp.message_handler(state=[States.SET_FILE,States.SET_NAME], commands="Cancel")
async def cancel(message:types.Message, state:FSMContext):
    await state.set_state(States.BASIC_STATE)
    await message.reply("Операция добавления  файла была успешно отменена")
    globals()["AUDIO_ID"] = ''



@dp.message_handler(state=[States.BASIC_STATE], commands=["Audios"])
async def get_all_audios(message:types.Message, state:FSMContext):
    names = await DB.get_all()
    if len(names) != 0:
        str = '\n'.join([a.get("name") for a in names])
        await message.reply(str)
    else:
        await message.reply("База даных пуста, вы можете добавить аудиофайл с помощью команды /Add")




@dp.message_handler(state=[States.BASIC_STATE],commands=['Voice'])
async def get_voice(message:types.Message, state:FSMContext):
    pattern = r"/Voice[ ]*([a-zA-Z0-9а-яА-Я ]+)"
    if len(message.text.split("/Voice")[-1]) == 0:
        await message.reply("Вы не указали название файла который вы хотите отправить")
    else:
        voice_name = re.match(pattern, message.text.strip()).group(1).strip()
        exist = await DB.check_if_exist(voice_name)
        if exist:
            voice_id = await DB.get_distinct(voice_name)
            try:
                await  message.reply_voice(voice_id)
            except utils.exceptions.TypeOfFileMismatch:
                await  message.reply_audio(voice_id)
        else:
            await message.reply("В базе нету файла с таким именем")

@dp.message_handler(state=[States.BASIC_STATE], commands=["Rename"])
async def rename_audio(message:types.Message, state:FSMContext):
    pattern = r"/Rename[ ]*([\d\D]+)--set_new"
    pattern_2 = "--set_new"
    pattern_3 = r"/Rename[ ]*[\d\D]+--set_new[ ]*([\d\D]+)"
    if len(message.text.split("/Delete")[-1]) == 0:
        await message.reply("Вы не указали название аудио которое вы хотите переименовать")
    elif not message.text.count(pattern_2) or len(message.text.split(pattern_2)[-1]) == 0:
        await message.reply("Вы не указали новое название для аудио которое вы хотите переименовать или ошиблись в вводе '--set_new' ")
    else:
        old_name = re.match(pattern, message.text).group(1).strip()
        exist = await DB.check_if_exist(old_name)
        if exist:
            new_name = re.match(pattern_3, message.text).group(1).strip()
            await DB.update(old_name, new_name)
            await message.reply(f"Файл '{old_name}' был успешно переименован в '{new_name}'")
        else:
            await message.reply("В базе нету файла с таким именем")







@dp.message_handler(state=[States.BASIC_STATE],commands=["Delete"])
async def delete_voice(message:types.Message, state:FSMContext):
    pattern = r"/Delete[ ]*([a-zA-Z0-9а-яА-Я ]+)"
    if len(message.text.split("/Delete")[-1]) == 0:
        await message.reply("Вы не указали название файла который вы хотите удалить")
    else:
        voice_name = re.match(pattern, message.text.strip()).group(1).strip()
        exist = await DB.check_if_exist(voice_name)
        if exist:
            await DB.delete(voice_name)
            await message.reply("Файл с именем {} был успешно удален".format(voice_name))
        else:
            await message.reply("В базе нету файла с таким именем")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)