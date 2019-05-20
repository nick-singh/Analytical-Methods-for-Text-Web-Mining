import mechanize, urllib2, time, datetime, re
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue, Pool, cpu_count
import pandas as pd

class Scraper():
    def __init__(self):
        self.base = "https://www.trinidadexpress.com/search/?"
        self.headers = ("User-agent","Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")
        self.basekeys = ['d1', 's', 'sd', 'l', 't', 'nsa']
        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.addheaders = [self.headers]

    def build_daily_search(self, keys = None, query = None):
        q_list = []
        for k in keys:
            q_list.append(str(k)+"="+str(query[k]))
        q = "&".join(q_list)
        return self.base+q

    def process_page(self, **args):
        q = args['query'] if 'query' in args.keys() else {
                                'd1':datetime.datetime.now().strftime('%Y-%m-%d'),
                                's':'start_time',
                                'sd':'desc',
                                'l': 100,
                                't':'article',
                                'nsa':'eedition'
                            }
        k = args['keys'] if 'keys' in args.keys() else self.basekeys
        url = self.build_daily_search(k, q)
        print url
        open_url = self.br.open(url)
        soup = BeautifulSoup(open_url.read(), 'html.parser')
        links = []
        content = soup.find(class_="results-container")
        link_containers = content.find_all('h3', {'class', "tnt-headline"})
        articles = []
        for link in link_containers:
            l = link.find('a')['href']
            article = self.process_link(l)
            articles.append(article)
        return articles

    def process_link(self, url_link):
        print "processing: ", url_link
        try:
            link = self.br.open("https://www.trinidadexpress.com"+url_link).read()
            soup = BeautifulSoup(link, 'html.parser')
            title = soup.find('h1', {'class', "headline"}).text.encode('ascii', 'ignore')
            author = soup.select('span[itemprop="author"]')
            dateCreated = soup.find('time', {'class', "asset-date text-muted"})
            imgUrl = soup.find('div', {'class','image'})
            data = {
                'url':url_link,
                'title': re.sub('\W+ ','', title),
                'author':author[0].text.encode('ascii', 'ignore') if len(author) > 0 else "undefined",
                'dateCreated': dateCreated['datetime'] if dateCreated is not None\
                                else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'imgUrl': imgUrl.find('img')['src'] if imgUrl is not None else "undefined"
            }
            article = soup.find('div', {'class':'asset-content subscriber-premium'}).find_all('p')
            article_text = ""
            for pgraph in article:
                article_text+=pgraph.text.encode('ascii', 'ignore').replace('\n','')
            if imgUrl is not None:
                caption = soup.find('figcaption', {'class', "caption"})
                data['caption'] = re.sub('\W+ ','', caption.text.encode('ascii', 'ignore')) \
                if caption is not None else "undefined"
            # print(data['imgUrl'])
            data['article_text'] = article_text
            return data
        except Exception as e:
            print e
            return {}


search = Scraper()

qry = {
        'd1':'2019-05-18',
        's':'start_time',
        'sd':'desc',
        'l': 10,
        't':'article',
        'nsa':'eedition'
    }

end_data = search.process_page(query=qry)
df = pd.DataFrame(end_data)
df.to_csv(qry['d1']+'-'+str(qry['l'])+'.csv', sep='^')
print "completed: ", category
