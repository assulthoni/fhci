import csv
import requests
import time
import tqdm
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

URL_BASE = 'https://rekrutmenbersama2024.fhcibumn.id'
URL_JOB = f'{URL_BASE}/job'
URL_LOAD_RECORD = f'{URL_BASE}/job/loadRecord'
URL_GET_DETAIL = f'{URL_BASE}/job/get_detail_vac'

headers = {
    'User-Agent' : 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
}


def requests_all_job():
    session = requests.Session()
    soupjob = BeautifulSoup(session.get(URL_JOB, headers=headers, verify=False).content)
    csrftoken = soupjob.find('input', dict(name='csrf_fhci'))['value']
    print(csrftoken)
    jobs = session.post(
        URL_LOAD_RECORD,
        data=dict(csrf_fhci=csrftoken, company='all'),
        headers=headers,
        verify=False
    )
    print(jobs.status_code)
    return jobs.json()


def parse_to_csv(data, path):
    keys = data[0].keys()
    with open(path, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def get_detail_jobs(job_id):
    session = requests.Session()
    soupjob = BeautifulSoup(session.get(URL_JOB, headers=headers, verify=False).content)
    csrftoken = soupjob.find('input', dict(name='csrf_fhci'))['value']
    detail = session.post(
        URL_GET_DETAIL,
        data=dict(csrf_fhci=csrftoken, id=job_id),
        headers=headers,
        verify=False
    )
    print(detail.status_code)
    print(detail.text)
    if detail.status_code == 200:
        return detail.json()
    return 0


def get_all_details(path):
    vacant_ids = []
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=",")
        for i, row in enumerate(reader):
            if i == 0:
                continue
            vacant_ids.append(row[0])
    print(len(vacant_ids))
    data = []
    for id in tqdm.tqdm(vacant_ids):
        try:
            datum = get_detail_jobs(id)
            if datum == 0:
                continue
            data.append(datum)
            time.sleep(0.1)
        except Exception as e:
            print("Err.. ", e)
            continue
    return data


if __name__ == '__main__':
    jobs = requests_all_job()
    print(len(jobs['data']['result']))
    parse_to_csv(jobs['data']['result'], 'data/all_jobs.csv')
    print("Sleeping...")
    time.sleep(5)
    details = get_all_details('data/all_jobs.csv')
    parse_to_csv(details, 'data/details.csv')