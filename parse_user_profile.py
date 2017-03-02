from bs4 import BeautifulSoup
import requests
import time
import json
from kafka import KafkaProducer
from pprint import pprint

headers = {
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
}
domain_name = 'https://www.zhihu.com'
user_url_prefix = 'https://www.zhihu.com/people/'
follower_page_dir = '/following'

def request_user_profile_page(username):
    url = user_url_prefix + username
    reply = requests.get(url, headers=headers)
    if reply.status_code == 200:
        soup = BeautifulSoup(reply.text, 'html.parser')

    def parse_user_profile_page(soup):
        profile_header = soup.find(id='ProfileHeader')
        with open("profile.html", 'wb+') as f:
            f.write(soup.prettify('utf-8'))

        json_string = soup.find('div', attrs={'data-state': True})['data-state']
        user_info = json.loads(json_string)['entities']['users'][username]

        info = {}

        #id
        info['id'] = user_info['id']
        print("id ", info['id'])

        #头像url
        info['avatarUrl'] = user_info['avatarUrl']

        #封面url
        info['coverUrl'] = user_info['coverUrl']

        #收藏数
        info['favoriteCount'] = user_info['favoriteCount']

        #获得点赞数
        info['voteupCount'] = user_info['voteupCount']

        #值乎?
        info['commercialQuestionCount'] = user_info['commercialQuestionCount']

        #关注专栏数
        info['followingColumnsCount'] = user_info['followingColumnsCount']

        #参与live数
        info['participatedLiveCount'] = user_info['participatedLiveCount']

        #关注的收藏夹数
        info['isAdvertiser'] = user_info['isAdvertiser']

        #被收藏次数
        info['favoritedCount'] = user_info['favoritedCount']

        #关注人数
        info['followerCount'] = user_info['followerCount']

        #关注话题数
        info['followingTopicCount'] = user_info['followingTopicCount']

        #关注问题数
        info['followingQuestionCount'] = user_info['followingQuestionCount']

        #商业信息
        info['business'] = user_info['business']['name']

        #live数
        info['hostedLiveCount'] = user_info['hostedLiveCount']

        #?
        info['thankToCount'] = user_info['thankToCount']

        #被知乎收藏的答案？
        info['markedAnswersCount'] = user_info['markedAnswersCount']

        #?
        info['thankFromCount'] = user_info['thankFromCount']

        #?
        info['voteToCount'] = user_info['voteToCount']

        #回答数
        info['answerCount'] = user_info['answerCount']

        #好像是分享数
        info['articlesCount'] = user_info['articlesCount']

        #昵称
        info['nick ']= user_info['name']

        #提问数
        info['questionCount'] = user_info['questionCount']

        #参与公共编辑数
        info['logsCount'] = user_info['logsCount']

        #获得感谢次数
        info['thankedCount'] = user_info['thankedCount']

        #性别
        info['gender'] = user_info['gender']

        #获取教育信息
        info['educations'] = []
        for item in user_info['educations']:
            edu_info = {'school':"Default-School-Name", "major":"Default-Major-Name"}
            edu_info['school'] = item['school']['name']
            edu_info['major'] = item['major']['name']
            info['educations'].append(edu_info)

        #获取公司信息
        employment_infos = []
        for item in user_info['employments']:
            job_info = {}
            job_info['company'] = item['company']['name']
            job_info['job'] = item['job']['name']
            employment_infos.append(job_info)
        info['employments'] = employment_infos

        return info

    return parse_user_profile_page(soup)

data = request_user_profile_page("excited-vczh")
d = json.dumps(data,sort_keys=True,indent=4)

producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

producer.send('zhihu_user_info', d)
