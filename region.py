import requests, os
import logging
from bs4 import BeautifulSoup
import hashlib
import pickle
from fake_useragent import UserAgent
import xlwt

logging.basicConfig(level=logging.INFO)

DIR = '/tmp/region'
BASE_URL = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019'
USER_AGENT = UserAgent().random

def fetch_url(url):
  url = '%s/%s' % (BASE_URL, url)
  my_md5 = hashlib.md5()
  my_md5.update(url.encode('utf-8'))
  digest = my_md5.hexdigest()
  filepath = '%s/%s' % (DIR, digest)

  if os.path.exists(filepath):
    return filepath
  else:
    with open(filepath, 'wb') as file:
      try:
        logging.info('fetch_url %s to %s' % (url, filepath))
        r = requests.get(url, headers = {'user-agent' : USER_AGENT})
        file.write(r.content)
        return filepath
      except Exception as e:
        logging.error(e)
        return None

def remove_url(url):
  url = '%s/%s' % (BASE_URL, url)
  my_md5 = hashlib.md5()
  my_md5.update(url.encode('utf-8'))
  digest = my_md5.hexdigest()
  filepath = '%s/%s' % (DIR, digest)
  os.remove(filepath)

def handle_decode_error(func):
  def wrapper(url):
    filepath = fetch_url(url)
    if filepath:
      with open(filepath, encoding='gb2312') as file:
        try:
          datas = func(file)
        except:
          remove_url(url)
          datas = None

    return datas

  return wrapper

@handle_decode_error
def get_province(file):
  datas = []
  soup = BeautifulSoup(file.read(), features="html5lib")
  for tr in soup.find_all('tr', class_='provincetr'):
    links = tr.find_all('a')
    for link in links:
      datas.append({'name': link.text, 'href': link['href']})
  
  return datas


@handle_decode_error
def get_city(file):
  datas = []
  soup = BeautifulSoup(file.read(), features="html5lib")
  for tr in soup.find_all('tr', class_='citytr'):
    link = tr.find_all('a')[-1]
    datas.append({'name': link.text, 'href': link['href']})

  return datas
  

@handle_decode_error
def get_country(file):
  datas = []
  
  soup = BeautifulSoup(file.read(), features="html5lib")
  for tr in soup.find_all('tr', class_='countytr'):
    links = tr.find_all('a')
    if len(links) == 2:
      link = links[-1]
      datas.append({'name': link.text, 'href': link['href']})

  return datas

def load(pickle_file):
  provinces = None
  if os.path.exists(pickle_file):
    with open(pickle_file, 'rb') as f:
      provinces = pickle.load(f)

  return provinces

def save(datas, pickle_file):
  with open(pickle_file, 'wb') as f:
    pickle.dump(datas, f)


def write_excel_xls(path, rows, headers):
  workbook = xlwt.Workbook()  # 新建一个工作簿
  
  index = len(rows)  # 获取需要写入数据的行数
  sheet = workbook.add_sheet('数据')  # 在工作簿中新建一个表格

  for j in range(0, len(headers)):
    sheet.write(0, j, headers[j])  # 像表格中写入数据（对应的行和列）

  for i in range(1, index):
    for j in range(0, len(rows[i])):
      sheet.write(i, j, rows[i][j])  # 像表格中写入数据（对应的行和列）
  workbook.save(path)  # 保存工作簿

if __name__ == '__main__':
  os.makedirs(DIR, exist_ok=True)
  datas = load('region.pkl')

  if not datas:
    datas = get_province('/index.html')
    save(datas, 'region.pkl')

  for province in datas:
    if not 'cities' in province or not province['cities']:
      cities = get_city(province['href'])
      province['cities'] = cities
      save(datas, 'region.pkl')

  for province in datas:
    for city in province['cities']:
      if not 'countries' in city or not city['countries']:
        countries = get_country(city['href'])
        city['countries'] = countries
        save(datas, 'region.pkl')

  rows = []
  for prov in datas:
    for city in prov['cities']:
      if city['countries']:
        for country in city['countries']:
          rows.append([prov['name'], city['name'], country['name']])
      else:
        logging.error('缺 %s 省 %s 市的区域数据' % (prov['name'], city['name']))

  write_excel_xls('country.xls', rows, ['省', '市', '区'])
