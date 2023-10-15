from jdatetime import datetime as jdatetime
from asyncio import run
from httpx import AsyncClient
from random import randint
from re import search
from rubpy import Client
from time import time

def detect_language(text):
    # تشخیص کاراکترهای فارسی با استفاده از عبارت منظم
    persian_pattern = r'[\u0600-\u06FF\u0750-\u077F\uFB8A\u067E\u0686\u0698]+'

    if search(persian_pattern, text):
        return 'Persian'
    else:
        return 'English'

async def get_date(client: Client, update: dict):
    now = jdatetime.now()

    shamsi_year = now.year
    shamsi_month = now.month
    shamsi_day = now.day

    shamsi_hour = now.hour
    shamsi_minute = now.minute
    shamsi_second = now.second

    await client.send_message(update.object_guid, f"• تاریخ شمسی: {shamsi_year}/{shamsi_month}/{shamsi_day}\n• ساعت شمسی: {shamsi_hour}:{shamsi_minute}:{shamsi_second}",
                              reply_to_message_id=update.last_message_id)

async def main():
    async with Client(session='MySelf') as client:
        me_guid: str = client._guid
        seen: list = []
        AsyncHTTP = AsyncClient()
        only_me = True

        while True:
            if len(seen) > 40:
                seen = []

            try:
                updates = await client.get_chats_updates(round(time()) - 100)
            except Exception as exc:
                print('Error in get updates:', exc)

            for update in updates.chats:
                try:
                    if update.abs_object.type in ['Group', 'User'] and update.last_message.type == 'Text':
                        if only_me:
                            if update.last_message.author_object_guid == me_guid:
                                pass
                            else:
                                continue

                        if update.last_message_id not in seen:
                            seen.append(update.last_message_id)
                            text: str = update.last_message.text

                            if text in ['.تاریخ', '.ساعت', '.زمان']:
                                await get_date(client, update)

                            elif text.startswith('.سلف'):
                                if update.last_message.author_object_guid == me_guid:
                                    if text.split(' ')[-1] == 'همه':
                                        only_me = False
                                        await client.send_message(update.object_guid, '**از الان به بعد قابلیتای سلف برا همه فعاله ♡_♡**', update.last_message_id)
                                    else:
                                        only_me = True
                                        await client.send_message(update.object_guid, '**الان دیگه سلف فقط برا خودت کار میکنه °~°**', update.last_message_id)

                            elif text.startswith('.بررسی'):
                                username = text.split('@')[-1]
                                if len(username) < 4:
                                    await client.send_message(update.object_guid, '**نام کاربری باید بیشتر از 4 کارکتر باشه *_***', update.last_message_id)
                                    continue
                                result = await client.check_user_username(username)
                                if result.exist:
                                    await client.send_message(update.object_guid, '**این یوزنیم گرفته شده -_-**', update.last_message_id)
                                else:
                                    await client.send_message(update.object_guid, '**این یوزنیم گرفته نشده ^-^**', update.last_message_id)

                            elif text.startswith('.هوایز'):
                                domain = text.split(' ')[-1]
                                if len(domain) < 3:
                                    await client.send_message(update.object_guid, '**دامنه باید بیشتر از 3 کارکتر باشه *_***', update.last_message_id)
                                    continue
                                response = await AsyncHTTP.get(f'http://api.codebazan.ir/whois/index.php?type=json&domain={domain}')
                                response = response.json()
                                owner, location, ip, address, dns = response.get('owner'), response.get('location'), response.get('ip'), response.get('address'), response.get('dns')
                                await client.send_message(update.object_guid, f'● Domain: {domain}\n\n• Owner: {owner or "None"}\n• ip: {ip or "None"}\n• location: {location or "None"}\n• address: {address or "None"}\n• dns1: {dns.get("1") or "None"}\n• dns2: {dns.get("2") or "None"}\n• dns3: {dns.get("3")}\n• dns4: {dns.get("4")}',
                                                            reply_to_message_id=update.last_message_id)

                            elif text == '.دانستنی':
                                response = await AsyncHTTP.get('http://api.codebazan.ir/danestani/')
                                await client.send_message(update.object_guid, f'**● دانستنی:**\n{response.text}', update.last_message_id)

                            elif text == '.ذکر':
                                response = await AsyncHTTP.get('http://api.codebazan.ir/zekr/')
                                await client.send_message(update.object_guid, f'**● ذکر امروز:**\n{response.text}', update.last_message_id)

                            elif text == '.حدیث':
                                response = await AsyncHTTP.get('http://api.codebazan.ir/hadis/')
                                await client.send_message(update.object_guid, f'**● حدیث:**\n{response.text}', update.last_message_id)

                            elif text == '.داستان':
                                response = await AsyncHTTP.get('http://api.codebazan.ir/dastan/')
                                await client.send_message(update.object_guid, f'**● داستان:**\n{response.text}', update.last_message_id)

                            elif text == '.بیو':
                                response = await AsyncHTTP.get('http://api.codebazan.ir/bio/')
                                await client.send_message(update.object_guid, f'**● بیوگرافی:**\n{response.text}', update.last_message_id)

                            elif text.startswith('.فونت'):
                                name = text.split(' ')[-1]
                                check_lang = detect_language(name)
                                response = await AsyncHTTP.get(f'http://api.codebazan.ir/font/?text={name}' if check_lang == 'English' else f'https://api.codebazan.ir/font/?type=fa&text={name}')
                                response = response.json().get('result') if check_lang == 'English' else response.json().get('Result')
                                await client.send_message(update.object_guid, f'**● فونت:**\n\n`{response.get(str(randint(1, 138) if check_lang == "English" else randint(1, 10)))}`', update.last_message_id)

                except Exception as exc:
                    print('An Error:', exc)

run(main())