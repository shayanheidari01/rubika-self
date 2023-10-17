from jdatetime import datetime as jdatetime
from aiofile import async_open as aiopen
from asyncio import run, create_task, sleep as aiosleep
from httpx import AsyncClient
from random import randint
from re import search
from rubpy import Client
from time import time

AsyncHTTP = AsyncClient()
only_me = True
speaker = False
my_before_answer = ''

def detect_language(text):
    persian_pattern = r'[\u0600-\u06FF\u0750-\u077F\uFB8A\u067E\u0686\u0698]+'
    return 'Persian' if search(persian_pattern, text) else 'English'

def create_triangle(text: str, height: int = 5):
    triangle = ''
    for i in range(1, height + 1):
        triangle += ' ' * (height - i)
        triangle += f'{text}' * (2 * i - 1)
        triangle += '\n'
    return triangle

def create_square(text: str, side_length: int = 5):
    square = ''
    for _ in range(side_length):
        square += text * side_length
        square += '\n'
    return square

async def get_date(client: Client, update: dict):
    now = jdatetime.now()
    shamsi_date = now.strftime('%Y/%m/%d')
    shamsi_time = now.strftime('%H:%M:%S')

    message = f"• تاریخ شمسی: {shamsi_date}\n• ساعت شمسی: {shamsi_time}"
    await client.send_message(update.object_guid, message, reply_to_message_id=update.last_message_id)

async def handle_username_check(text, update, client):
    username = text.split('@')[-1]
    if len(username) < 4:
        return await client.send_message(update.object_guid, '**نام کاربری باید بیشتر از 4 کارکتر باشه *_***', update.last_message_id)
    result = await client.check_user_username(username)
    if result.exist:
        await client.send_message(update.object_guid, '**این یوزنیم گرفته شده -_-**', update.last_message_id)
    else:
        await client.send_message(update.object_guid, '**این یوزنیم گرفته نشده ^-^**', update.last_message_id)

async def handle_whois(text, update, client):
    domain = text.split(' ')[-1]
    if len(domain) < 3:
        return await client.send_message(update.object_guid, '**دامنه باید بیشتر از 3 کارکتر باشه *_***', update.last_message_id)
    response = await AsyncHTTP.get(f'http://api.codebazan.ir/whois/index.php?type=json&domain={domain}')
    response = response.json()
    owner, location, ip, address, dns = response.get('owner'), response.get('location'), response.get('ip'), response.get('address'), response.get('dns')
    await client.send_message(update.object_guid, f'● Domain: {domain}\n\n• Owner: {owner or "None"}\n• ip: {ip or "None"}\n• location: {location or "None"}\n• address: {address or "None"}\n• dns1: {dns.get("1") or "None"}\n• dns2: {dns.get("2") or "None"}\n• dns3: {dns.get("3")}\n• dns4: {dns.get("4")}',
                                reply_to_message_id=update.last_message_id)

async def handle_danestani(update, client):
    response = await AsyncHTTP.get('http://api.codebazan.ir/danestani/')
    await client.send_message(update.object_guid, f'**● دانستنی:**\n{response.text}', update.last_message_id)

async def handle_zekr(update, client):
    response = await AsyncHTTP.get('http://api.codebazan.ir/zekr/')
    await client.send_message(update.object_guid, f'**● ذکر امروز:**\n{response.text}', update.last_message_id)

async def handle_hadis(update, client):
    response = await AsyncHTTP.get('http://api.codebazan.ir/hadis/')
    await client.send_message(update.object_guid, f'**● حدیث:**\n{response.text}', update.last_message_id)

async def handle_dastan(update, client):
    response = await AsyncHTTP.get('http://api.codebazan.ir/dastan/')
    await client.send_message(update.object_guid, f'**● داستان کوتاه:**\n{response.text}', update.last_message_id)

async def handle_bio(update, client):
    response = await AsyncHTTP.get('http://api.codebazan.ir/bio/')
    await client.send_message(update.object_guid, f'**● بیوگرافی:**\n{response.text}', update.last_message_id)

async def handle_self_command_safely(text, update, me_guid, client):
    global only_me
    if update.last_message.author_object_guid == me_guid:
        if text.split(' ')[-1] == 'همه':
            only_me = False
            await client.send_message(update.object_guid, '**از الان به بعد قابلیتای سلف برا همه فعاله ♡_♡**', update.last_message_id)
        else:
            only_me = True
            await client.send_message(update.object_guid, '**الان دیگه سلف فقط برا خودت کار میکنه °~°**', update.last_message_id)

async def handler_set_speaker(text, update, client):
    global speaker
    if update.last_message.author_object_guid == client._guid:
        if text.split(' ')[-1] == 'فعال':
            speaker = True
            await client.send_message(update.object_guid, '**از الان به بعد خودکار جواب میدم و شایدم چرت و پرت زیاد بگم 😜😂**', update.last_message_id)
        else:
            speaker = False
            await client.send_message(update.object_guid, '**بازم دهنمو چسب زدی؟ 😞😂**', update.last_message_id)

async def handler_chatgpt(text, update, client):
    try:
        response = await AsyncHTTP.get('https://haji-api.ir/Free-GPT3/?text='+text[5:].strip())
        response = response.json()
        await client.send_message(update.object_guid, '**★‌ چت جی‌پی‌تی:**\n\n' + response.get('result').get('answer'), update.last_message_id)
    except Exception as exc:
        print('error in chatgpt handler:', exc)

async def handle_self_command(text, update, client):
    global only_me
    global speaker
    me_guid = client._guid
    print(text)

    if text in ['.راهنما', '.کمک', '.help']:  
        async with aiopen(r'./help.txt', 'r') as file:
            await client.send_message(update.object_guid, await file.read(), update.last_message_id)
    elif text in ['.تاریخ', '.ساعت', '.زمان']:
        await get_date(client, update)
    elif text.startswith('.سلف'):
        await handle_self_command_safely(text, update, me_guid, client)
    elif text.startswith('.بررسی'):
        await handle_username_check(text, update, client)
    elif text.startswith('.هوایز'):
        await handle_whois(text, update, client)
    elif text == '.دانستنی':
        await handle_danestani(update, client)
    elif text == '.ذکر':
        await handle_zekr(update, client)
    elif text == '.حدیث':
        await handle_hadis(update, client)
    elif text == '.داستان':
        await handle_dastan(update, client)
    elif text == '.بیو':
        await handle_bio(update, client)
    elif text.startswith('.مکعب متحرک '):
        await handle_movable_cube(text, update, client)
    elif text.startswith('.صدا'):
        await handle_text_to_voice(text, update, client)
    elif text.startswith('.فونت'):
        await handler_font(text, update, client)
    elif text.startswith('.سخنگو'):
        await handler_set_speaker(text, update, client)
    elif text.startswith('.ربات'):
        await handler_chatgpt(text, update, client)

async def handle_movable_cube(text, update, client):
    out = create_square(text[12:].strip())
    split_out = out.splitlines()
    message_update = None

    for i in range(len(split_out)):
        if i == 0:
            message_update = await client.send_message(update.object_guid, split_out[i], update.last_message_id)
            continue
        await client.edit_message(update.object_guid, message_update.message_id, split_out[i].strip() * randint(i, len(split_out)))
        await aiosleep(0.3)

    await client.edit_message(update.object_guid, message_update.message_id, out)

async def handle_instagram_link(text, update, client):
    url = text.replace('.اینستاگرام', '').strip()
    response = await AsyncHTTP.get(url.replace('instagram', 'ddinstagram'))
    await client.send_file(update.object_guid, await response.aread(), file_name='photo.jpg', reply_to_message_id=update.last_message_id)

async def handle_text_to_voice(text, update, client):
    text = text[4:].strip()
    response = await AsyncHTTP.get(f'https://haji-api.ir/text-to-voice/?text={text}&Character=FaridNeural')
    url = response.json().get('results').get('url')
    response = await AsyncHTTP.get(url)
    await client.send_music(update.object_guid, await response.aread(), file_name=url.split('/')[-1], reply_to_message_id=update.last_message_id)

async def handler_font(text, update, client):
    name = text.split(' ')[-1]
    check_lang = detect_language(name)
    response = await AsyncHTTP.get(f'http://api.codebazan.ir/font/?text={name}' if check_lang == 'English' else f'https://api.codebazan.ir/font/?type=fa&text={name}')
    response = response.json().get('result') if check_lang == 'English' else response.json().get('Result')
    await client.send_message(update.object_guid, f'**● فونت:**\n\n`{response.get(str(randint(1, 138) if check_lang == "English" else randint(1, 10)))}`', update.last_message_id)

async def handler(client: Client, update: dict):
    global only_me
    global speaker
    global my_before_answer
    text = update.last_message.text
    if text == my_before_answer:
        return None

    try:
        if text.startswith('.'):
            return await handle_self_command(text, update, client)
        elif speaker:
            response = (await AsyncHTTP.get('https://haji-api.ir/sokhan/', params={'text': text})).text
            if '<!DOCTYPE html>' in response:
                return None
            my_before_answer = response
            await client.send_message(update.object_guid, response, update.last_message_id)
    except Exception as exc:
        print('An Error:', exc)

async def main():
    async with Client(session='MySelf', timeout=20) as client:
        me_guid = client._guid
        seen = []
        await client.send_message(me_guid, '**● ربات سلف فعال شد!**\n• با استفاده از دستور `.راهنما` میتونی تمام قابلیتا و سرگرمیای ربات رو ببینی 😎👌\n**• شایان حیدری**')

        while True:
            if len(seen) > 40:
                seen = []

            try:
                updates = await client.get_chats_updates(round(time()) - 200)
            except Exception as exc:
                print('Error in get updates:', exc)

            for update in updates.chats:
                if update.abs_object.type in ['Group', 'User'] and update.last_message.type == 'Text':
                    if only_me:
                        if update.last_message.author_object_guid == me_guid:
                            pass
                        else:
                            continue

                    if update.last_message_id not in seen:
                        create_task(handler(client, update))
                        seen.append(update.last_message_id)

run(main())