from http import cookiejar
from bs4 import BeautifulSoup
import requests
import time
import traceback
import os.path


headers = {
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
}

url_index = 'https://www.zhihu.com/'
url_profile = 'https://www.zhihu.com/settings/profile'
COOKIE_FILE = 'my_cookies'

cookie = cookiejar.CookieJar()
session = requests.Session()
session.cookies = cookiejar.LWPCookieJar(COOKIE_FILE)

#解析 _xsrf字段
def get_xsrf():
    url_login_zhihu = 'https://www.zhihu.com/'
    reply = session.get(url_login_zhihu, headers=headers, verify=False)
    if reply.status_code == 200:
        session.cookies.save()
        with open('login_page.html', 'wb+') as f:
            f.write(reply.content)

        soup = BeautifulSoup(reply.text)
        _xsrf = soup.body.input['value']
        return _xsrf
    else:
        return False

#处理登录验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()

    captcha = input("please input the captcha\n>")
    return captcha

#查看个人资料
def isLogin():
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, allow_redirects=False).status_code
    if int(login_code) == 200:
        return True
    else:
        return False

#验证登录结果
def check_login_result(request_reply):
    if request_reply.status_code == 200:
        content = eval(request_reply.text)
        #print('post reply content: ', content)

        if content['r'] == 0:
            return True
        elif content.has_key('errcode'):
            print('返回错误： 错误码-', content['errcode'], '  提示信息-', content['msg'])
            return False
        else:
            print('返回异常')
            return False
    else:
        print('返回失败, 错误码-', request_reply.status_code)
        return False

#通过登录请求登录
def post_login_request(email, password, _xsrf, *, captcha = ''):
    post_data = {
        '_xsrf': _xsrf,
        'email': email,
        'password': password,
    }

    if captcha != '':
        post_data['captcha'] = captcha

    url_login = 'https://www.zhihu.com/login/email'
    reply = session.post(url_login, data=post_data, headers=headers, verify=False)
    return reply

#通过cookies登录
def login_with_cookie():
    try:
        session.cookies.load(ignore_discard=True)
        profile_page = session.get(url_profile, headers = headers, allow_redirects = False)
        if profile_page.status_code == 200:
            session.cookies.save()
            with open('profile.html', 'wb+') as f:
                f.write(profile_page.content)
            return True
        else:
            print('login with cookie fail, error code: ', profile_page.status_code)
            return False
    except Exception as f:
        print('Can not load ', COOKIE_FILE)
        return False

#通过用户信息登录
def login_with_user_info():
    _xsrf = get_xsrf()
    captcha = get_captcha()

    try:
        reply = post_login_request('okjklgo@gmail.com', 'buxiangjizhu', _xsrf, captcha=captcha)
        if check_login_result(reply) == True:
            session.cookies.save()
            return True

        else:
            print('check login result: NOT LOGIN')
            print('post reply is: \n', reply)
            with open('post_reply', 'wb+') as f:
                f.write(reply.text)
            return False

    except Exception as e:
        print('Exception occur: ', e)
        return False

def get_index():
    try:
        index_page = session.get(url_index, headers=headers, allow_redirects = False)
        if index_page.status_code == 200:
            session.cookies.save()
            return index_page.content
        else:
            print('HTTP GET on ', url_index, ' fail, error: ', index_page.status_code)
            return False

    except Exception as e:
        print('Exception occur: ', e)
        return False

def do():
    print('尝试cookies登录...')
    if login_with_cookie() == False:
        print('尝试使用用户信息登录...')
        if login_with_user_info() == False:
            print('已尝试所有登录方法后任然无法登录')
            return False

    print('登录成功')
    result = get_index()
    if result != False:
        with open('index.html', 'wb+') as f:
            f.write(result)
    else:
        print('未能成功获取到用户首页')

do()