import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InputMediaPhoto, InputMediaVideo
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import CommandStart
from aiogram.enums import ContentType
import threading
from gigachat import GigaChat
from dotenv import load_dotenv
from server import run as run_flask
import os

load_dotenv()

# Токены ботов
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv("CHANEL_ID")   
API_TOKEN = os.getenv('API_TOKEN')                     

PROMPT = '''Ты — профессиональный редактор игровых и поп-культурных материалов. Твоя задача — улучшать статьи и новости, делая их увлекательными и современными, но без использования разметки (никаких звездочек, жирного шрифта и т.д.).

Правила редактирования:
Корректура:
— Исправь грамматику, пунктуацию и стилистику.
— Удали лишние слова, сохранив суть.

Стиль:
— Добавь игровой сленг и отсылки к играм/кино (например: "ачивка", "респавн"), но без перегруза.
— Сделай текст динамичным: короткие абзацы, списки, риторические вопросы.
— Сохрани дружелюбный тон с юмором, как в разговоре с другом.

SEO и вовлечение:
— Включи ключевые слова (например: "гайд по Starfield", "трейлер Marvel") естественно.
— Добавь призывы к действию: "Какой класс в Diablo IV тебе зашел? Ждем в комментах!"

Контроль качества:
— Проверь факты (даты, названия, имена). Если не уверен — оставь пометку.
— Предложи альтернативные заголовки (пример: вместо "Новости игры" → "Зачем все стримят этот безумный боссфайт?").

Пример (без лишних символов!):
Исходный текст:
"В игре обновление: добавлен режим выживания с новыми врагами."

Редакция:
"Разработчики закатили апдейт почище цитадели в Half-Life: теперь в режиме выживания вас ждут полчища монстров. Сможете продержаться до финальной волны?"

Что важно:
— Никаких звездочек, кавычек для выделения или форматирования.
— Если исходник скучный — добавь драйва через глаголы и эмоции ("взорвать мету", "эпичный сюжет"), но не искажай факты.
— Пиши коротко, ярко и по делу. Если сомневаешься в стиле — сделай текст нейтральным, но живым.'''

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# class IsForwarded(Filter):
#     """Фильтр для проверки пересланных сообщений."""
    
#     async def __call__(self, message: Message) -> bool:
#         return message.forward_from is not None

# def remove_patterns(text, patterns):
#     for pattern in patterns:
#         text = re.sub(pattern, '', text)
#     return text

# Функция для обращения к нейросети
async def rephrase_text(text):
    with GigaChat(credentials=API_TOKEN, verify_ssl_certs=False) as giga:
        response = giga.chat(f'{PROMPT} Вот текст -[{text}]')
    answer_text = response.choices[0].message.content
    #answer_text = remove_patterns(remove_text, personal.patterns)
    return answer_text


@dp.message(CommandStart())
async def Star_Doing(message: types.Message):
    #buttons = [types.KeyboardButton(text="Рерайт"), types.KeyboardButton(text="QR-code")]
    #keyboard_start = types.ReplyKeyboardMarkup(keyboard_start=buttons)
    #await message.answer(f'Дороу, {message.from_user.first_name}. Выбирай, что хочешь?', reply_markup=keyboard_start)
    await message.answer(f'Дратути, {message.from_user.first_name}. Этот бот должен отредактивровать твой текст. Использует нейросеть Сбербанка GigaChat')

@dp.message(F.content_type == ContentType.TEXT, ~F.media_group_id)
async def text_handler(message: types.Message):
    if message.media_group_id or message.caption:
        return
    
    edited_text = f"📝 {message.text.upper()} [ОБРАБОТАНО]"
    await message.answer(edited_text)

# 2. Обработчик одного изображения
@dp.message(F.content_type == ContentType.PHOTO, ~F.media_group_id)
async def photo_handler(message: types.Message):
    edited_text = await rephrase_text(message.caption)
    await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=edited_text)

# 3. Обработчик видео
@dp.message(F.content_type == ContentType.VIDEO, ~F.media_group_id)
async def video_handler(message: types.Message):
    edited_text = await rephrase_text(message.caption)
    # await message.answer_video(
    #     video=message.video.file_id, 
    #     caption=edited_text
    # )
    await bot.send_video(CHANNEL_ID, message.video.file_id, caption=edited_text)


# Обработчик пересланного сообщения
# @dp.message()
# async def handle_forwarded_message(message: types.Message):
    
#     try:
#         source_info = ""
        
#         # if message.forward_from_chat:
#         #     if message.forward_from_chat.username:
#         #         source_info = f"Источник: Телеграм канал @{message.forward_from_chat.username}"
#         #     elif message.forward_from_chat.title:
#         #         source_info = f"Источник: Телеграм канал {message.forward_from_chat.title}"
        
#         if message.media_group_id is not None:
#             # Если сообщение входит в группу мультимедиа, собираем все части группы
#             media_group = await bot.get_media_group(
#                 chat_id=message.chat.id,
#                 message_ids=[message.message_id]
#             )

#             media_files = []
#             caption = ""

#             for msg in media_group:
#                 file = await msg.photo[-1].get_file()
#                 media_files.append(InputMediaPhoto(file.file_id, caption=caption))
#                 caption = await rephrase_text(msg.caption or "") + "\n\n" + source_info

#             # Отправляем медиафайлы в канал
#             await bot.send_media_group(CHANNEL_ID, media_files)
#         else:
#             photo = message.photo[-1] if message.photo else None
#             video = message.video if message.video else None
#             document = message.document if message.document else None

#             if photo:
#                 # Получаем файл самого большого размера фото
#                 file_id = photo.file_id
                
#                 # Перефразируем текст и отправляем в канал
#                 caption = await rephrase_text(message.caption) + "\n\n" + source_info
#                 await bot.send_photo(CHANNEL_ID, photo=file_id, caption=caption)
#             elif video:
#                 # Аналогично загружаем видео
#                 file_id = video.file_id

#                 # Перефразируем текст и отправляем видео в канал
#                 caption = await rephrase_text(video.caption) if video.caption else "" + "\n\n" + source_info
#                 await bot.send_video(CHANNEL_ID, video=file_id, caption=caption)
#             else:
#                 text = await rephrase_text(message.text) + "\n\n" + source_info
#                 await bot.send_message(CHANNEL_ID, text)
#     except Exception as e:
#         await message.reply(f"Произошла ошибка: {e}")





if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем бота
    try:
        asyncio.run(dp.start_polling(bot))
    except (KeyboardInterrupt, SystemExit):
        print('Бот остановлен!')