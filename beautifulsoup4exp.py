import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import datetime
import time
from multiprocessing import Process, Pool
import os
import random
pause_date=datetime.date(2019,8,1)

def has_href_and_title(tag):
    '''
    用来排除董秘问答的帖子的董秘问答超链接，只有标题的a标签有title属性
    '''
    return tag.has_attr('href') and tag.has_attr('title')

def already_crawled(code,num):
    stk_file='E:/爬虫数据/爬虫/{}'.format(code)
    list=os.listdir(stk_file)
    if '{code}_{num}.json'.format(code=code,num=str(num)) in list:
        return True
    else:
        return False

def finish_crawl(code):
    stk_file='E:/爬虫数据/爬虫/{}'.format(code)
    list=os.listdir(stk_file)
    if 'done.txt' in list:
        return True
    else:
        return False

def get_post_data(code,start):
    
    #科创板不需要加截止时间条件
    
    
    while(True):
        if already_crawled(code, start):
            print('already crawled {code} {num}'.format(code=code, num=start))
            start+=1
            continue
        total_content=[]
        
        url='http://guba.eastmoney.com/list,{code},f_{num}.html'.format(code=str(code),num=str(start))
        #print(str(url))
        #time.sleep(5)
        res = requests.get(url, timeout=None)
        print('--get daze {}'.format(str(url)))
        soup = BeautifulSoup(res.text,'lxml')
        #判断是不是没帖子了
        if soup.find('div',class_='noarticle'):
            t=open('done.txt','w',encoding='utf-8')
            t.close()
            break
        #如果传入列表参数,Beautiful Soup会将与列表中任一元素匹配的内容返回
        posts=soup.find_all('div',class_='articleh normal_post') #可以直接匹配class_="articleh normal_post"，但是用正则匹配多值的时候就不行了
        #posts=soup.find('div',attrs={'id':'articlelistnew'}).find_all('div',class_='articleh normal_post')
        #print(posts)
        print("crawling {}".format(str(url)))
        for post in posts:
            
            if len(post.find('span',class_='l3 a3').contents)>1:#排除问董秘的帖子和其他悬赏回答帖子，这些帖子的class="l3 a3"包含超过一个子标签
                continue
            #href也是a这个tag的一个属性，tag的属性的操作方法与字典相同:tag['class']
            post_url=post.find(has_href_and_title)['href']
            #print(post_url)
            post_comment=post.find(class_='l2 a2').string
            if post_comment==0:
                continue
            post_title=post.find('a').string
            post_view=post.find(class_='l1 a1').string
            time.sleep(random.uniform(1,2))
            post_page=BeautifulSoup(requests.get('http://guba.eastmoney.com'+post_url,timeout=None).text,'lxml')
            #用正文页面的完整格式的日期生成datetime变量
            if post_page.find('div',class_='zwfbtime'):
                post_date=datetime.date.fromisoformat(post_page.find('div',class_='zwfbtime').string.split()[1])
            else:
                post_date='None'
                t=open('E:/爬虫数据/errors/{code}_{num}.txt'.format(code=code,num=start),'w',encoding='utf-8')
                t.write(post_url)
                t.close()
            post_content=''
            if post_page.find('div',class_='stockcodec .xeditor'):
                post_content_list=post_page.find('div',class_='stockcodec .xeditor').find_all('p')

            #如果一个tag仅有一个子节点,那么这个tag也可以使用 .string 方法,输出结果与当前唯一子节点的 .string 结果相同:
            #如果tag包含了多个子节点,tag就无法确定 .string 方法应该调用哪个子节点的内容, .string 的输出结果是 None :
                for p in post_content_list:
                    for child in p.children:
                        if(child.string):
                            post_content+=child.string
            else:
                t=open('E:/爬虫数据/errors/{code}_{num}.txt'.format(code=code,num=start),'a',encoding='utf-8')
                t.write(post_url)
                t.close()   
            if '期权开户指引' in post_content:
                print('失敗した失敗した失敗した')
                t=open('E:/爬虫数据/errors/{code}_{num}.txt'.format(code=code,num=start),'a',encoding='utf-8')
                t.write(post_url)
                t.close()
                continue
            dic={
                'url':post_url,
                'title':post_title,
                'view':post_view,
                'comment':post_comment,
                'date':str(post_date),
                'content':post_content
            }
            total_content.append(dic)
        f=open('{code}_{num}.json'.format(code=str(code),num=start),'w',encoding='utf-8')
        f.write(json.dumps(total_content,indent=0,ensure_ascii=False))
        f.close()
        print("done with crawling {}".format(str(url)))
        start+=1
    
data=pd.read_csv('科创板.csv')
codes=data['code'].tolist()


    #stk_file='./{}'.format(code)
    #os.mkdir(stk_file)
    #进入新文件夹
    #os.chdir(stk_file)
    #返回上级目录
def main(code):
    stk_file='E:/爬虫数据/爬虫/{}'.format(code)
    start=1
    if not os.path.exists(stk_file):
        os.mkdir(stk_file)
    #进入新文件夹
    os.chdir(stk_file)
    #返回上级目录
    if not finish_crawl(code):
        get_post_data(code,start)
    os.chdir('E:/爬虫数据/爬虫')

if __name__=='__main__':

    p=Pool(4)
    p.map(main,codes)

    #for code in codes:
        #main(code)


