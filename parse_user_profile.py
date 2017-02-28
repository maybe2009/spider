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

t0 = time.clock()

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

#获取
#这种方式提取的关注用户数据是有瑕疵的，关注的用户会包含用户自己，不过这里不去纠正了，因为爬虫从页面获取的数据本身就可以当做是不可信数据，
#这里只负责把信息挖出来，清洗是后面的事
def extract_following_info_from_page(soup):
    try:
        # 所有的用户信息都在一个div标签的data-state属性中并以json格式存储
        json_string = soup.find('div', attrs={'data-state': True})['data-state']
        following = json.loads(json_string)['entities']['users']
        return following
    except Exception as e:
        print('解析页面获取关注列表时出现异常:', e)
        return None

#获取下一页的页码，先找到当前页，再去找下一个button较为稳妥，信息是最新的
def extract_next_page_number(soup):
    try:
        current_page_tag = soup.find(class_='Button PaginationButton PaginationButton--current Button--plain')
        next_page_tag = current_page_tag.next_sibling
        if next_page_tag != None:
            next_page_num = next_page_tag.string
            print('current ', current_page_tag.string, ' next ', next_page_num)
            return next_page_num
        else:
            return None
    except Exception as e:
        print('获取页码时出现异常:', e)
        return None

def get_all_follower_info(user_name):
    try:
        all_following = {}
        next_page = user_url_prefix + user_name + follower_page_dir
        while next_page != None:
            reply = requests.get(next_page, headers=headers, verify=False)
            if reply.status_code == 200:
                soup = BeautifulSoup(reply.text, 'html.parser')

                following = extract_following_info_from_page(soup)
                if following == None:
                    break

                all_following.update(following)

                next_page_number = extract_next_page_number(soup)
                if next_page_number == None:
                    break
                next_page = user_url_prefix + user_name + follower_page_dir + "?page=" + next_page_number
        return all_following
    except Exception as e:
        print('获取用户关注信息时出现异常:', e)


#following = get_all_follower_info('wang-ming-jie-7')
#producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092',
                         #value_serializer=lambda v: json.dumps(v).encode('utf-8'))

'''
count = 1
for k, v in following.items():
    try:
        nick = v['name']
        url = user_url_prefix + v['urlToken']
        portrait_url = v['avatarUrl']
        print('Num.', count, '昵称:', nick, '个人页:', url, '头像url', portrait_url)
        count = count + 1
    except TypeError as f:
        print('获取用户信息出现错误，该用户将被跳过, 详细信息:', v)
'''

"{\"school\": \"华南理工大学（SCUT）\", \"major\": \"软件学院\"}"
data1 = {"school": "华南理工大学（SCUT）", "major": "软件学院"}
data = request_user_profile_page("excited-vczh")
d1 = json.dumps(data,sort_keys=True,indent=4)
pprint(data)
#jd = json.loads(data,  object_hook=json.JSONObject)
#pprint("data \n", jd)
# def deprecated():
#     if reply.status_code == 200:
#         soup = BeautifulSoup(reply.text, 'html.parser')
#         with open('following.html', 'wb+') as f:
#             f.write(soup.prettify('utf-8'))
#
#         profile_following_tags = soup.find(class_='List')
#         if profile_following_tags['id'] != 'Profile-following':
#             print('解析出错')
#
#         #print(profile_following_tags.prettify())
#         following_list_tags = profile_following_tags.find_all(class_ = 'List-item')
#         print('size ', len(following_list_tags))
#
#         for follower in following_list_tags:
#             t0 = time.clock()
#             #获取关注者名字以及关注者个人页url
#             content_tag = follower.find(class_ = "ContentItem PortraitItem-content")
#             user_link_tag = content_tag.find(class_ = 'UserLink-link')
#             user_name = user_link_tag.string
#             user_url = user_link_tag['href']
#
#             #获取关注者头像
#             portrait_tag = follower.find(class_ = 'PortraitItem')
#             img_url = portrait_tag.img['src']
#             img_user_name = portrait_tag.img['alt']
#             img_name = user_name + '_' + img_url.split('com/', 1)[1]
#
#             print(user_name)
#             print(user_url)
#             print(img_url)
#             print(img_name)
#
#             new_url = domain_name + user_url
#
#             reply = requests.get(img_url, headers = headers, verify = False)
#             if reply.status_code == 200:
#                 with open(img_name, 'wb+') as f:
#                     print('write to ', img_name)
#                     f.write(reply.content)
#             else:
#                 print('download image error')
#
#             t1 = time.clock()
#             print('time used: ', t1 - t0)
#
#     else:
#         print('request error ', reply.status_code)

t1 = time.clock()

print('total time = ', t1 - t0)