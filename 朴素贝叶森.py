import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold

from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier

import json
import jieba as jb
import os


#小白也能看懂的朴素贝叶斯文本分类
pos='positive.txt'
neg='negative.txt'
def dummy_fun(doc):
    return doc
def load_corpus():
    pos_list=[]
    neg_list=[]
    #pos_list=['帖子1', '帖子2', ...]
    with open(pos,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                pos_list.append(line)
    
    with open(neg,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            
            neg_list.append(line)
    balance_len = min(len(pos_list),len(neg_list))
    texts=pos_list+neg_list
    labels=[1]*balance_len+[0]*balance_len
    return texts, labels

def test_accuracy(text_clf, data, target):
    #做十折交叉验证，把样本分成十分，9份用来训练，1份用来测试
    kf=KFold(n_splits=10, shuffle=True, random_state=233)

    score=[]

    for train, test in kf.split(data): #注意返回的是下标
        train_data=[data[i] for i in train]
        train_test=[data[i] for i in test]
        target_data=[target[i] for i in train]
        target_test=[target[i] for i in test]
        #拟合模型
        text_clf.fit(train_data,target_data)
        #测试模型
        score.append(text_clf.score(train_test,target_test))
    print(score)
    return score

#一个pipeline把文本向量化等等到拟合模型的步骤全部用一个.fit()做好，只要更换用的分类器'clf'就可以测试不同模型


def load_predict_data():
    path='./save'
    #save_path='./tag'
    file_list=os.listdir(path)

    jb.load_userdict('user_dict.txt')

    stopwords=set()
    with open('baidu_stopwords.txt','r',encoding='utf-8') as f:
        for word in f:
            stopwords.add(word.strip())
    result={}
    for file in file_list:
        with open(os.path.join(path,file),'r',encoding='utf-8') as f:
            js_dict=json.load(f)
        
        for i in range(len(js_dict)):
            
            js_dict[i]['jb']=jb.lcut(js_dict[i]['title']+js_dict[i]['content'])
    
        #with open(os.path.join(save_path,file),'w',encoding='utf-8') as f:
        #    f.write(json.dumps(js_dict,indent=0,ensure_ascii=False))

        result[file]=js_dict
    
    return result

def load_discrepancy_data():
    path='./save'
    #save_path='./tag'
    file_list=os.listdir(path)

    #jb.load_userdict('user_dict.txt')

    stopwords=set()
    with open('baidu_stopwords.txt','r',encoding='utf-8') as f:
        for word in f:
            stopwords.add(word.strip())
    result={}
    for file in file_list:
        with open(os.path.join(path,file),'r',encoding='utf-8') as f:
            js_dict=json.load(f)
        
        for i in range(len(js_dict)):
            
            js_dict[i]['jb_title']=jb.lcut(js_dict[i]['title'])
            js_dict[i]['jb_content']=jb.lcut(js_dict[i]['content'])
        #with open(os.path.join(save_path,file),'w',encoding='utf-8') as f:
        #    f.write(json.dumps(js_dict,indent=0,ensure_ascii=False))

        result[file]=js_dict
    
    return result

def predict_raw_data():
    text_clf= Pipeline([
        ('vect_transform',TfidfVectorizer(analyzer='word',lowercase=False)),
        ('clf', MultinomialNB())
    ])

    data, target=load_corpus()

    text_clf.fit(data, target)

    X=load_predict_data()
    for key,value in X.items():
        print('现在股票是',key)
        test=[i['jb'] for i in value]
        for i in range(len(test)):
            sentence=' '.join(test[i])
            sentence=[sentence]
            value[i]['predict']=float(text_clf.predict(sentence)[0])

        savepath='./tag'
        with open(savepath+'/'+key,'w',encoding='utf-8') as f:
            f.write(json.dumps(value,indent=0,ensure_ascii=False))

def predict_discrepancy():
    #看title和content不一样的
    text_clf= Pipeline([
        ('vect_transform',TfidfVectorizer(analyzer='word',lowercase=False)),
        ('clf', MultinomialNB())
    ])

    data, target=load_corpus()

    text_clf.fit(data, target)

    X=load_discrepancy_data()
    count=0
    f=open('output.txt','w',encoding='utf-8')
    for key,value in X.items():
        print('现在股票是',key)
        f.write(key)
        f.write('\n')
        test_title=[i['jb_title'] for i in value]
        for i in range(len(test_title)):
            sentence=' '.join(test_title[i])
            sentence=[sentence]
            value[i]['predict_title']=float(text_clf.predict(sentence)[0])

        test_content=[i['jb_content'] for i in value]
        for i in range(len(test_content)):
            sentence=' '.join(test_content[i])
            sentence=[sentence]
            value[i]['predict_content']=float(text_clf.predict(sentence)[0])

        for  i in range(len(value)):
            if value[i]['content']=='':
                continue
            if value[i]['predict_title']!=value[i]['predict_content']:
                count+=1
                f.write(str(value[i]['predict_title']))
                f.write('  ')
                f.write(value[i]['title'])
                f.write('\n')
                f.write(str(value[i]['predict_content']))
                f.write('  ')
                f.write((value[i]['content']))
                f.write('\n')
                f.write('\n')
        #savepath='./tag1'
        #with open(savepath+'/'+key,'w',encoding='utf-8') as f:
        #    f.write(json.dumps(value,indent=0,ensure_ascii=False))
    f.close()
    print(count)

classifiers = [
        ('LinearSVC', svm.LinearSVC()),
        ('LogisticReg', LogisticRegression()),
        ('SGD', SGDClassifier()),
        ('MultinomialNB', MultinomialNB()),
        ('KNN', KNeighborsClassifier()),
        ('DecisionTree', DecisionTreeClassifier()),
        ('RandomForest', RandomForestClassifier()),
        ('AdaBoost', AdaBoostClassifier(base_estimator=LogisticRegression()))
    ]
result={}
for (name,clf) in classifiers:

    text_clf= Pipeline([
            ('vect_transform',TfidfVectorizer(analyzer='word',lowercase=False)),
            ('clf', clf)
        ])

    data,target=load_corpus()

    score=test_accuracy(text_clf,data,target)
    result[name]=score
df=pd.DataFrame(result)
df.to_csv('多种分类算法比较.csv')
'''
n=len(X)//5

x_train=X[n:]
x_test=X[:n]
y_train=y[n:]
y_test=y[:n]

vectorizer = TfidfVectorizer(analyzer='word',
                            lowercase=False)

vectorizer.fit(x_train)

x_train=vectorizer.transform(x_train)
x_test=vectorizer.transform(x_test)

clf=MultinomialNB()

clf.fit(x_train, y_train)

print(clf.score(x_test, y_test))
'''
#看得到吗
#看得到吗#看得到吗#看得到吗#看得到吗#看得到吗#看得到吗#看得到吗#看得到吗
#看得到吗#看得到吗#看得到吗