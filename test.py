from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import json
import codecs

today = datetime.datetime.now()
# today = datetime.datetime(2022, 9, 20)
# today = datetime.datetime(2022, 9, 23)
day = today.strftime('%d')
month = today.strftime('%b')
month2 = today.strftime('%m')
year = today.strftime('%Y')
year = str(int(year) + 1286)
filename = 'data.json'
filename2 = 'uuid.json'
# filename = '/home/4N0NYM/bot/data.json'

print(today)
month = month.upper()
url = "https://community.elitedangerous.com/de/galnet/"+day +"-" + month + "-" + year
content = urlopen(url).read()
print(url)

soup = BeautifulSoup(content, 'lxml')
text = soup.find_all('div', class_='article')

my_json = []


def check(uuid):
        uuids = []
        with open(filename2, 'r', encoding='UTF8') as datei:
                for zeile in datei:
                        data = json.loads(zeile)
                        uuids.append(data['message_nr'])

        # print(uuids)
        if uuid in uuids:
                return 1
        else:
                my_json = {
                        'message_nr': uuid
                }
                if my_json:
                        with codecs.open(filename2, 'a+', encoding='utf-8', errors='ignore') as f:
                                data = json.dumps(my_json, ensure_ascii=False)
                                f.write(data)
                                f.write('\n')
                return 0



def write_json_file():
        for count, t in enumerate(reversed(text)):
                UUID = int(str(day) + str(month2) + str(year) + str(count))
                if check(UUID) != 1:
                        headline = t.find_all('h3')
                        for h in headline:
                                head = h.text
                        l_head = t.find_all('p', class_="small")
                        for l in l_head:
                                datum = l.text
                        gn = t.find_all('p')
                        for i in gn:
                                tex = i.text
                        # print(len(head) + len(datum) + len(tex) + len(url))
                        tex = tex + '\r\n' + url
                        my_json = {
                                'message_nr': UUID,
                                'header': head,
                                'date': datum,
                                'content': tex
                                }
                        if my_json:
                                with codecs.open(filename, 'w', encoding='utf-8', errors='ignore') as f:
                                        data = json.dumps(my_json, ensure_ascii=False)
                                        f.write(data)
                                        f.write('\n')
                # break
write_json_file()

