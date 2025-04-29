import io
import requests
from bs4 import BeautifulSoup
import os
from pdfminer.high_level import extract_text
import time
import random

each_file_name = ''
each_file_pmcid = ''
txt_save_path = ''
name = ''
current_line = 0
origin_pdf_path = ''
current_crawler = 1
switch = 'false'

current_directory = os.getcwd()
# input_data 的完整路徑
input_data_directory = os.path.join(current_directory, 'input_data')

pdf_save_path = os.path.join(current_directory, 'output_data/pdf')

# 以檔案紀錄目前爬取到的檔案行數
file_current_crawler_path = os.path.join(current_directory, 'current_crawler.txt')

# 確保 current_crawler.txt 存在
if not os.path.exists(file_current_crawler_path):
    with open(file_current_crawler_path, 'w') as f:
        f.write('1')

# 讀取當前資料號碼
with open(file_current_crawler_path, 'r') as f:
    current_crawler = int(f.read())

# pmcid 的網址
def find_url(PMC_url):
    send_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    response = requests.get(PMC_url, headers=send_headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            href = link.get('href')
            if href.startswith('/pmc/articles/') and href.endswith('.pdf'):
                return "https://www.ncbi.nlm.nih.gov" + href
    else:
        print("請求失敗，狀態碼：", response.status_code)

# pmcid網址 對應的 pdf 下載
def download_pdf(save_path, pdf_name, pdf_url):
    send_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    response = requests.get(pdf_url, headers=send_headers)
    if response.status_code == 200:
        bytes_io = io.BytesIO(response.content)
        os.makedirs(save_path, exist_ok=True)  # 確保目錄存在
        with open(os.path.join(save_path, f"{pdf_name}.PDF"), mode='wb') as f:
            f.write(bytes_io.getvalue())
            print(f'{pdf_name}.PDF 下載成功！')
    else:
        print(f'無法下載 {pdf_name}.PDF ！')

# pdf 轉成 txt 檔
def pdf_to_txt(pdf_path):
    global txt_save_path

    try:
        text = extract_text(pdf_path)
        os.makedirs(os.path.dirname(txt_save_path), exist_ok=True)  # 確保目錄存在
        with open(txt_save_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'第 {current_crawler - 1} 資料轉換成功！\n')
    except Exception as e:
        print(f"PDF 轉換失敗: {e}")

# 搜尋檔名、並提取PMCID
def search_file_pmcid(target_file):
    global current_crawler
    global each_file_name
    global each_file_pmcid
    global current_line
    global name
    global txt_save_path
    global origin_pdf_path
    global pdf_save_path
    global switch
    global current_directory

    for root, dirs, files in os.walk(input_data_directory):
        for file in files:
            if file == target_file:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line:
                            with open(file_current_crawler_path, 'w') as f:
                                f.write(str(1))
                            print('資料整理完成!')
                            break
                        if line.startswith(str(current_crawler) + '. '):
                            current_crawler += 1
                            current_line = 1
                            switch = 'true'
                            with open(file_current_crawler_path, 'w') as f:
                                f.write(str(current_crawler))
                        elif line.startswith('PMCID'):
                            if switch == 'true':
                                switch = 'false'
                                each_file_pmcid = line.split()[-1]
                                each_file_name = name if len(name) > 1 else each_file_pmcid
                                print('檔名 = ' + each_file_name)
                                print('PMCID = ' + each_file_pmcid + '\n')

                                origin_pdf_path = os.path.join(current_directory, f'output_data/pdf/{each_file_name}.pdf')
                                txt_save_path = os.path.join(current_directory, f'output_data/txt/{each_file_name}.txt')
                                pdf_name = each_file_name

                                pdf_url = find_url("https://www.ncbi.nlm.nih.gov/pmc/articles/" + each_file_pmcid + '/')

                                if pdf_url:
                                    download_pdf(pdf_save_path, pdf_name, pdf_url)
                                    pdf_to_txt(origin_pdf_path)
                                else:
                                    print("找不到 PDF 鏈接，跳過該筆資料。")
                        elif current_line == 2:
                            name = line
                            current_line += 1
                        else:
                            current_line += 1

if __name__ == '__main__':
    target_file = os.path.join(current_directory, "joint_discomfort.txt")  # 指定想讀取的txt檔

    while True:
        try:
            search_file_pmcid(target_file)
        except Exception as e:
            print("程式出現異常:", e)
            wait_time = random.randint(100, 600)
            print("等待", wait_time, "秒...")
            time.sleep(wait_time)
            continue
        except KeyboardInterrupt:
            current_crawler -= 1
            with open(file_current_crawler_path, 'w') as f:
                f.write(str(current_crawler))
            print('\n')
            print('當前讀到的資料為第', str(current_crawler), '筆')
            break