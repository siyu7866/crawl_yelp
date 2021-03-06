import pandas as pd
import numpy as np
import os 
import requests
import re
import time 
import random
from bs4 import BeautifulSoup
from bs4.element import ResultSet
import urllib

def getReviewContent(result: ResultSet, index: int, soup: BeautifulSoup):
    name_list = []
    rating_list = []
    date_list = []
    review_content_list = []
    rounde_rating = soup.find_all(class_ = 'i-stars__373c0___sZu0')[0]['aria-label'].split()[0]
    for i in range(len(result)):
        review_number = len(result[i].find_all(class_ = 'comment__373c0__Nsutg'))
        if review_number > 1:
            name = result[i].find(class_ = 'fs-block css-m6anxm').text
            rating = result[i].find_all(class_ = 'i-stars__373c0___sZu0')
            date = result[i].find_all(class_ = 'css-e81eai')
            review_content = result[i].find_all(class_='comment__373c0__Nsutg')
            for j in range(review_number):
                name_list.append(name)
                rating_list.append(rating[j]['aria-label'].split()[0])
                date_list.append(date[j].text)
                review_content_list.append(review_content[j].text)
        else:
            name = result[i].find(class_ = 'fs-block css-m6anxm').text
            rating = result[i].find(class_ = 'i-stars__373c0___sZu0')['aria-label'].split()[0]
            date = result[i].find(class_ = 'css-e81eai').text
            review_content = result[i].find(class_='comment__373c0__Nsutg').text

            name_list.append(name)
            rating_list.append(rating)
            date_list.append(date)
            review_content_list.append(review_content)
    return {'doctorID': [index]*len(name_list), 
            'username': name_list, 
            'rating': rating_list, 
            'date_of_review': date_list, 
            'review_content': review_content_list, 
            'rounded_rating': [rounde_rating]*len(name_list)}

def haveReview(result: ResultSet):
    if len(result) == 0:
        return False
    else:
        return True

def getCurrentUrl(url: str):
    try:
        res = urllib.request.urlopen(url)
        finalurl = res.geturl()
        if finalurl==url:
            pass
        else:
            url = finalurl
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return url

def main():
    temp_list = []
    df_url = pd.read_excel('file path of excel having urls')

    for i in range(268, 296):
        url = df_url['URL'][i]
        url = getCurrentUrl(url)
        print("the " + str(i) + "th URL is being crawled")
        try:
            response = requests.get(url).text
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        time.sleep(random.randint(20, 30))
        # Use BeautifulSoup to parse HTML
        soup = BeautifulSoup(response,'html.parser')
        result = soup.findAll(class_="review__373c0__3MsBX")
        index = 0
        while(haveReview(result)):
            temp_dict = getReviewContent(result, i, soup)
            temp_list.append(temp_dict)
            index += 1
            try:
                response = requests.get(url + "?start=" + str(index*10)).text
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            # Use BeautifulSoup to parse HTML
            soup = BeautifulSoup(response,'html.parser')
            result = soup.findAll(class_="review__373c0__3MsBX")
        print("the " + str(i) + "th URL is finished")
    
    df = pd.DataFrame(temp_list[0])
    for i in range(1, len(temp_list)):
        tmp_df = pd.DataFrame(temp_list[i])
        df = df.append(tmp_df, ignore_index=True)
    df.to_csv('file path to save data as csv', index=False)

if __name__ == "__main__":
    main()