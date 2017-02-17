from bs4 import BeautifulSoup
import requests
import time
import json
from pprint import pprint

headers = {
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
}
domain_name = 'https://www.zhihu.com'
user_url_prefix = 'https://www.zhihu.com/people/'
follower_page_dir = '/following'

t0 = time.clock()

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

following = get_all_follower_info('wang-ming-jie-7')
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