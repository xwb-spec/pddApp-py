# -*- coding: utf-8 -*-
import time
import requests
import json
import hashlib
import execjs.runtime_names

"""
pip3 install execjs
npm i jsdom -g
"""
# python2 和 python3的兼容代码
try:
    # python2 中
    import cookielib
    print(f"user cookielib in python2.")
except:
    # python3 中
    import http.cookiejar as cookielib
    print(f"user cookielib in python3.")


class PingDuoDuoSpider(object):
    """
    拼多多加密解析
    """

    def __init__(self):
        # 初始化
        print('引擎', execjs.get().name)

    def encryPassword(self, password):
        with open("encryp.js", "r", encoding="utf-8") as f:
            ctx = execjs.compile(f.read())
        encryPass = ctx.call("encryPassword", password)
        return encryPass

    def antiContent(self, url):
        with open("merge.js", "r", encoding="utf-8") as f:
            ctx = execjs.compile(f.read())
        c = ctx.call("get_anti", url)
        return c

# session代表某一次连接
pSession = requests.session()
# 因为原始的session.cookies 没有save()方法，所以需要用到cookielib中的方法LWPCookieJar，这个类实例化的cookie对象，就可以直接调用save方法。
pSession.cookies = cookielib.LWPCookieJar(filename="Cookies.txt",)

userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
headers = {
    "origin": "https://mms.pinduoduo.com",
    "Referer": "https://mms.pinduoduo.com/login/",
    'User-Agent': userAgent,
    'Content-type': 'application/json'
}

def verifyCaptcha(token):
    # 获取图形码
    postUrl1 = "https://apiv2.pinduoduo.net/api/phantom/obtain_captcha"
    pdd = PingDuoDuoSpider()
    postData = {"anti_content": pdd.antiContent(postUrl1),
                "captcha_collect": "",
                "verify_auth_token": token,
                }
    responseRes = pSession.post(postUrl1, data=json.dumps(postData), headers=headers)
    responseRes = responseRes.json()
    if responseRes["code"] == 0:
        print("获取图形码图片成功")

    # 提交解密
    postUrl2 = "https://apiv2.pinduoduo.net/api/phantom/user_verify"
    postData = {"anti_content": pdd.antiContent(postUrl2),
                "captcha_collect": "",
                "verify_auth_token": token,
                "verify_code": 111,
                }
    responseRes = pSession.post(postUrl2, data=json.dumps(postData), headers=headers)
    responseRes = responseRes.json()  # 返回数据 {"code":0,"leftover":9,"result":true}
    if responseRes["code"] == 0:
        print("图形验证成功，开始登录..")
    else:
        print("图形验证失败")

    # 成功后开始登录

# 模仿 登录
def pLogin(account, password):
    print("开始模拟登录")
    postUrl = "https://mms.pinduoduo.com/janus/api/auth"
    pdd = PingDuoDuoSpider()
    antiContent = pdd.antiContent(postUrl)
    print(antiContent)
    riskSign = "username="+account+"&password="+password+"&ts="+str(round(time.time() * 1000))
    hl = hashlib.md5()
    hl.update(riskSign.encode(encoding='utf-8'))
    m = hl.hexdigest()
    print(m)
    encryPass = pdd.encryPassword(password)
    postData = {"username": account,
                "password": encryPass,
                "passwordEncrypt": True,
                "timestamp": int(round(time.time() * 1000)),
                # "crawlerInfo": antiContent,# anti-content
                "riskSign": m,
                "sign": "",
                "verificationCode": ""
                }
    responseRes = pSession.post(postUrl, data=json.dumps(postData), headers=headers)
    # 无论是否登录成功，状态码一般都是 statusCode = 200
    print(f"statusCode = {responseRes.status_code}")
    print(f"text = {responseRes.text}")
    responseRes = responseRes.json()
    if responseRes["success"] == True:
        print("登录成功，保存cookies。")
        pSession.cookies.save(ignore_discard=True, ignore_expires=True)
    elif responseRes["errorCode"] == 54001:
        token = responseRes["result"]["verifyAuthToken"]
        print("开始验证图形码")
        verifyCaptcha(token)






# 通过访问个人中心页面的返回状态码来判断是否为登录状态
# def isLoginStatus():
#     routeUrl = "https://mms.pinduoduo.com/earth/api/primeGiftPack/inWhiteList"
#     # 下面有两个关键点
#         # 第一个是header，如果不设置，会返回500的错误
#         # 第二个是allow_redirects，如果不设置，session访问时，服务器返回302，
#         # 然后session会自动重定向到登录页面，获取到登录页面之后，变成200的状态码
#         # allow_redirects = False  就是不允许重定向
#     responseRes = pSession.get(routeUrl, headers=headers, allow_redirects=False)
#     print(responseRes.text)
#     print(f"isLoginStatus = {responseRes.status_code}")
#     if responseRes.status_code != 200:
#         return False
#     else:
#         return True


if __name__ == "__main__":
	# 第一步：尝试使用已有的cookie登录
    pSession.cookies.load()
    # isLogin = isLoginStatus()
    # print(f"is login pinduoduo = {isLogin}")
    # if isLogin == False:
    #     # 第二步：如果cookie已经失效了，那就尝试用帐号登录
    #     print(f"cookie失效，用户重新登录...")
    pLogin("18617311540", "Xue3233603")
    cookie = requests.utils.dict_from_cookiejar(pSession.cookies)
    print(cookie)
    # pdd = PingDuoDuoSpider()
    # antiContent = pdd.antiContent(postUrl)

    resp = pSession.get("https://mms.pinduoduo.com/earth/api/primeGiftPack/inWhiteList", headers=headers,
                        allow_redirects=False)
    print(f"resp.status = {resp.status_code}")
    print(f"text = {resp.text}")
