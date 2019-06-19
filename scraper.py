from requests import get
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import json
import os

mobile_indeed = 'https://www.indeed.com/m/'
num_pages = 10
query = 'fullstack'
location = 'San+Francisco+Bay+Area%2C+CA'


def get_soup(url):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup


def grab_job_links(soup):
    urls = list()
    for link in soup.find_all('h2', {"class": "jobTitle"}):
        partial_url = link.a.get('href')
        url = mobile_indeed + partial_url
        urls.append(url)
    return urls


def get_job_tags(description):
    
    description = description.lower()

    tags = []
    tag_list = [
                'JavaScript', 'HTML', 'CSS', 'Java', 'Bash', 'Python', 'C#', 'PHP', 'C++', 'TypeScript', 
                'Ruby', 'Swift', 'Assembly', 'Objective-C', 'Kotlin', 'Scala', 'Groovy', 
                'Perl', 'Node.js', 'Angular', 'React', '.NET', 'Spring', 'Django', 'TensorFlow', 'Flask', 
                'Xamarin', 'Spark', 'Hadoop', 'PyTorch', 'MySQL', 'SQL', 'PostgreSQL', 'MongoDB', 'SQLite', 
                'Redis', 'Elasticsearch', 'MariaDB', 'Oracle', 'Memcached', 'DynamoDB', 'RDS', 'Cassandra', 
                'Linux', 'Android', 'AWS', 'Mac', 'WordPress', 'iOS', 'Firebase', 'Azure', 'Heroku'
                ]

    for tag in tag_list:
        if tag.lower() in description:
            tags.append(tag)
    
    return tags
        

def get_posting(url):
    soup = get_soup(url)

    p = soup.find_all('p')    

    # Check if there is a url to job apply page.
    # Only scraping job posts with apply url and without salary.
    apply_url = None
    for l in p:
        if l.find('span', {'class': 'salary'}):
            return None
        if l.find('a') and l.find('a').getText() == 'View job':
            apply_url = l.find('a')['href']
    if not apply_url:
        return None

    title = soup.find('font', {'size': '+1'}).getText()
    location = soup.find('span', {'class': 'location'}).getText()
    
    info = soup.find('p').getText()
    company = info.split('-')[-2].split('\n')[-1].strip()
    
    description = soup.find('div', {'id': 'desc'}).getText()

    newline = [i for i in range(len(description)) if description[i] == '\n']
    description = description[:newline[-2]]

    return to_dict(title, company, location, apply_url, description, url)


def to_dict(title, company, location, apply_url, description, indeed_url):
    template = {'title': title,
                'company': company,
                'location': location,
                'apply_url': apply_url,
                'description': description,
                'tags': get_job_tags(description),
                'indeed_url': indeed_url}
    return template


urls = []
for i in range(1, num_pages+1):
    num = (i-1) * 10
    base_url = mobile_indeed + 'jobs?q={}&l={}&start={}&sort=date'.format(query, location, num)
    try:
        soup = get_soup(base_url)
        urls += grab_job_links(soup)
    except Exception as e:
        continue

if os.path.exists('------'):     # replace ------ with existed record path
    tojson = json.load(open('jobs.json', 'r'))
else:
    tojson = dict()

for url in urls:
    
    # get the unique part of the indeed url as key
    ukey = url.split('=')[1]

    if ukey in tojson:
        continue
    job = get_posting(url)
    if job:
        tojson[ukey] = job
    sleep(3)

with open('####', 'w+') as f:     # replace ##### with your target location
    json.dump(tojson, f, separators=(',',':'), indent=4)