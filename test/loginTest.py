# -*- coding: utf-8 -*-

import requests
import json
import time
from test.PinDuoDuo import PingDuoDuoSpider
# python2 和 python3的兼容代码
try:
    # python2 中
    import cookielib
    print(f"user cookielib in python2.")
except:
    # python3 中
    import http.cookiejar as cookielib
    print(f"user cookielib in python3.")

# session代表某一次连接
mafengwoSession = requests.session()
# 因为原始的session.cookies 没有save()方法，所以需要用到cookielib中的方法LWPCookieJar，这个类实例化的cookie对象，就可以直接调用save方法。
mafengwoSession.cookies = cookielib.LWPCookieJar(filename = "mafengwoCookies.txt")

userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
header = {
    # "origin": "https://passport.mafengwo.cn",
    "Referer": "https://mms.pinduoduo.com",
    'User-Agent': userAgent,
    'Content-type': 'application/json',
}


# 马蜂窝模仿 登录
def mafengwoLogin(account, password):
    print("开始模拟登录马蜂窝")
    postUrl = "https://mms.pinduoduo.com/janus/api/auth"
    pdd = PingDuoDuoSpider(password)
    encryPass = pdd.make()
    postData = {"username":account,
                "password": encryPass,
                "passwordEncrypt":True,
                "verificationCode":"3333333",
                # "mobileVerifyCode":"",
                "sign":"",
                # "touchevent":
                #     {
                #         "mobileInputEditStartTime":1661865178711,
                #         "mobileInputEditFinishTime":1661865180444,
                #         "mobileInputKeyboardEvent":"0|0|0|-24668",
                #         "passwordInputEditStartTime":1661865180448,
                #         "passwordInputEditFinishTime":1661865181334,
                #         "passwordInputKeyboardEvent":"0|0|0|193-135-137-81-130",
                #         "captureInputEditStartTime":"","captureInputEditFinishTime":"",
                #         "captureInputKeyboardEvent":"",
                #         "loginButtonTouchPoint":"789,559",
                #         "loginButtonClickTime":1661865181434
                #     },
                "fingerprint":
                    {
                        "innerHeight":798,
                        "innerWidth":845,
                        "devicePixelRatio":2,
                        "availHeight":877,
                        "availWidth":1404,
                        "height":900,
                        "width":1440,
                        "colorDepth":30,
                        "locationHref":"https://mms.pinduoduo.com/login/?redirectUrl=https%3A%2F%2Fmms.pinduoduo.com%2F",
                        "clientWidth":845,
                        "clientHeight":883,
                        "offsetWidth":845,
                        "offsetHeight":883,
                        "scrollWidth":2451,
                        "scrollHeight":883,
                        "navigator":
                            {
                                "appCodeName":"Mozilla",
                             "appName":"Netscape",
                             "hardwareConcurrency":4,
                                "language":"zh-CN",
                                "cookieEnabled":True,
                                "platform":"MacIntel",
                                "doNotTrack":None,
                                "ua":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                                "vendor":"Google Inc.",
                                "product":"Gecko",
                                "productSub":"20030107",
                                "mimeTypes":"f5a1111231f589322da33fb59b56946b4043e092",
                                "plugins":"387b918f593d4d8d6bfa647c07e108afbd7a6223"
                            },
                        # "referer":"https://www.google.com/",
                        "timezoneOffset":-480},
                "riskSign":"477b2815b3c4c31327548f1454d7cab0",
                "timestamp":int(round(time.time() * 1000)),
                "crawlerInfo":"0apAfa5e-wCE0oKJXO8-cMEWYkcYcGdSIqgJspQFfRHImquhdam2EMsaA73w_-Atziepq9JpzsZd6qGAKG34e2wHSrqCbvywUFfTDBvhM3cDIsATzeA_-URglUF3RW13R_MeRDK8aAFK-TzK_k7V2DF8PPv1aSr1V139wBBs19Eoq_eHPUlWr5AHMMPzVCD-FFk-KVk-FUEzvVELV1k-wFk-fUkzVCEBjCgn0VglX8Du5laXIlxUtBZj0Ayt5XMfj6WvXi9TmXJXpUqIx_ylXnkoplhf0v69_ZCb2RHgtsCk22hk2KhI1MCzs4TUa1A-c_uzkfhk-xce8x-Sl6OgAGISLlTU3-u1c4A-KxuILMCMsBdM3c1D8VCS-m9CCI2Zz-fweFTGTYkgTzczwgsqFF32A-wAkE275UVNer-JMLcsUdAzd3AKhMBwwzRsMLvaVjg13oC0Ch_NhfxhWpNyQ_mv62bGK2oqIeotThJi7WaxdCf_Jut0JmqnMuXOrvutD1nHAMuoR8l92Xc-eEnlAmJy"}
    # 使用session直接post请求
    responseRes = mafengwoSession.post(postUrl, data=json.dumps(postData), headers=header)
    # 无论是否登录成功，状态码一般都是 statusCode = 200
    print(f"statusCode = {responseRes.status_code}")
    print(f"text = {responseRes.text}")
    # 登录成功之后，将cookie保存在本地文件中，好处是，以后再去获取马蜂窝首页的时候，就不需要再走mafengwoLogin的流程了，因为已经从文件中拿到cookie了
    mafengwoSession.cookies.save()


# 通过访问个人中心页面的返回状态码来判断是否为登录状态
def isLoginStatus():
    routeUrl = "https://mms.pinduoduo.com/mallcenter/changeAccountInfo/accountSetting/accountInfo"
    # 下面有两个关键点
        # 第一个是header，如果不设置，会返回500的错误
        # 第二个是allow_redirects，如果不设置，session访问时，服务器返回302，
        # 然后session会自动重定向到登录页面，获取到登录页面之后，变成200的状态码
        # allow_redirects = False  就是不允许重定向
    responseRes = mafengwoSession.get(routeUrl, headers = header, allow_redirects = False)
    print(f"isLoginStatus = {responseRes.status_code}")
    if responseRes.status_code != 200:
        return False
    else:
        return True


if __name__ == "__main__":
	# 第一步：尝试使用已有的cookie登录
    mafengwoSession.cookies.load()
    isLogin = isLoginStatus()
    print(f"is login mafengwo = {isLogin}")
    if isLogin == False:
        # 第二步：如果cookie已经失效了，那就尝试用帐号登录
        print(f"cookie失效，用户重新登录...")
        mafengwoLogin("18617311540", "Xue3233603")

    resp = mafengwoSession.get("https://mms.pinduoduo.com/mallcenter/changeAccountInfo/accountSetting/accountInfo", headers = header, allow_redirects = False)
    print(f"resp.status = {resp.status_code}")
    print(f"text = {resp.text}")
