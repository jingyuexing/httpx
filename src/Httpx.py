# -*- coding: utf-8 -*-
# @Author: admin
# @Date:   2022-04-17 13:58:03
# @Last Modified by:   admin
# @Last Modified time: 2022-04-17 18:07:08

from typing import Dict,Any, Literal, Optional, Union,Generic,TypeVar
import requests
from pydantic import BaseModel
from requests import Response
import json
from loguru import logger
from requests.cookies import RequestsCookieJar

T = TypeVar('T')

class RequestDecorator:
    @staticmethod
    def Query(url= ""):
        def wapper(func):
            func(url)
        return wapper
    
    @staticmethod
    def Path(url= ""):
        def wapper(func):
            func(url)
        return wapper
    @staticmethod
    def Get(url= ""):
        def wapper(func):
            func(url)
        return wapper

    @staticmethod
    def Header(headers = {}):
        def wapper(func):
            func(headers)
        return wapper

    @staticmethod
    def Post(url= ""):
        def wapper(func):
            func(url)
        return wapper

    @staticmethod
    def Put(url= ""):
        def outWapper(func):
            def wapper(*args, **kw):
                func(*args,**kw)
            return wapper
        return outWapper

    @staticmethod
    def Options(url=""):
        def wapper(func):
            func(url)
        return wapper

    @staticmethod
    def Delete(url=""):
        def wapper(func):
            return func(url)
        return wapper

class Query:
    def __init__(self, query):
        self.query = query
    def __call__(self,func):
        def wapper(*args, **kw):
            func(*args,**kw)
        return wapper

class Param:
    def __init__(self, param):
        self.param = param
    def __call__(self,func):
        def wapper(*args, **kw):
            func(*args,**kw)
        return wapper

class Cookies:
    """docstring for Cookies"""
    cookie = ""
    query = {}

    def __init__(self, cookies=''):
        self.parserCookies(cookies=cookies)
        self.cookie = self.toString()

    def setCookies(self, key, value):
        self.query[key] = value
        self.cookie = self.toString()

    def getCookies(self, key):
        return self.query[key]

    def getCookiesAll(self):
        return self.cookie

    def parserCookies(self, cookies=''):
        cookies = cookies.replace(" ", "")
        for x in cookies.split(";"):
            key, value = tuple(x.split("="))
            self.query[key] = value

    def __str__(self):
        keyWithValue = []
        for key in dict.keys(self.query):
            keyWithValue.append("{}={};".format(key, self.query[key]))
        return ";".join(keyWithValue)

    def replaceCookies(self, old='', new=''):
        oldCookies = Cookies(old)
        newCookies = Cookies(new)
        for key in dict.keys(newCookies.query):
            oldCookies.setCookies(key, newCookies.getCookies(key))
        return oldCookies.toString()

class Path:
    def __init__(self, url):
        self.url = url
    def __call__(self,func):
        def wapper(*args, **kw):
            func(*args,**kw)
        return wapper
class Request:
    url:str
    cookies:Optional['RequestsCookieJar'] = None
    auth:Optional[Any]
    header:Optional[Dict[str,str]]
    method:str
    json:Optional[Union['BaseModel',Dict[str,Any]]] = None
    form:Optional[Dict[str,Any]]
    path:Optional[Dict[str,Any]]
    query:Optional[Dict[str,Any]]
    def __init__(self,
        method,
        url='',
        query=None,
        path=None,
        cookie:Optional[Dict[str,Any]]=None,
        header:Optional[Dict[str,Any]]=None,
        auth:Optional[Any]=None,
        json:Optional[Union['BaseModel',Dict[str,Any]]] = None,
        form:Optional[Dict[str,Any]]=None
    ) -> None:
        self.method = method
        self.url = url
        self.auth = auth
        self.query = query
        self.path = path
        self.json = json
        self.form = form
        self.header = header
        self.cookies = self.parseCookie(cookie)
        self.parsePath(self.path)
    def parseCookie(self,cookies:Optional[Union[Dict[str,Any],str]] = None):
        if(cookies != None):
            if isinstance(cookies,str):
                cookiesInstance = Cookies(cookies=cookies)
                self.cookies = self.parseCookie(cookiesInstance.query)
            else:
                cookiesJar = RequestsCookieJar()
                for key in cookies:
                    cookiesJar.set(key,cookies[key])
                return cookiesJar
    def parsePath(self,path):
        if path != None:
            for name in path:
                self.url.replace(f":{name}",str(path[name]),1)
    def __call__(self, func) -> Any:
        def wapper(*args,**kw):
            response = requests.request(
                method=self.method,
                url=self.url,
                params=self.query,
                headers=self.header,
                cookies=self.cookies,
                json=self.json,
                data=self.form
            )
            func(response,*args,**kw)
        return wapper

class Get(Request):
    def __init__(self, url:str,path:Dict[str,Union[str,bool,int,float]]={}, query:Dict[str,Union[str,bool,int,float]]={}):
        self.url = url
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            response = requests.get(self.url, params=self.query)
            if response.status_code == 200:
                return func(response, *args, **kwargs)
            else:
                raise Exception('Failed to get data from server')
        return wrapper

class Post(Generic[T]):
    def __init__(self, url,query=None,json:T=None,auth=None,form:Any = None):
        self.url = url
        self.query = query
        self.json = json
        self.auth = auth
        self.form = form
    def __call__(self,func):
        def wapper(*args, **kw):
            response = requests.post(
                self.url, 
                params=self.query
            )
            if response.status_code == 200:
                return func(response, *args, **kw)
            else:
                raise Exception('Failed to get data from server')
        return wapper

class Put(Request):
    def __init__(self, url):
        self.url = url
    def __call__(self,func):
        def wapper(*args, **kw):
            response = requests.request(method="PUT",url=self.url, params=self.url)
            func(response,*args,**kw)
        return wapper

class Options(Request):
    def __init__(self, url):
        self.url = url
    def __call__(self,func):
        def wapper(*args, **kw):
            response = requests.request(method="OPTIONS",url=self.url, params=self.url)
            func(response,*args,**kw)
        return wapper



class Patch(Request):
    def __init__(self,
        url='',
        query:Optional[Dict[str,Any]]=None,
        path:Optional[Dict[str,Any]]=None,
        cookie:Optional[Dict[str,Any]] = None,
        json:Optional[Union[Dict[str,Any],'BaseModel']] = None,
        headers:Optional[Dict[str,Any]] = None,
        form:Optional[Dict[str,Any]] = None
    ):
        self.path = path
        self.url = url
        self.query = query
        self.path = path
        self.headers = headers
        self.form =form
        self.json = json
        self.parseCookie(cookie)
    def __call__(self,func):
        def wapper(*args, **kw):
            response = requests.request(
                method="PATCH",
                url=self.url,
                params=self.query,
                cookies=self.cookies,
                headers=self.headers,
                json=self.json,
                data=self.form

            )
            func(response,*args,**kw)
        return wapper

class Delete(Request):
    def __init__(self, url):
        self.url = url
    def __call__(self,func):
        def wapper(*args, **kw):
            response = requests.request(
                method="DELETE",
                url=self.url,
                params=self.url
            )
            func(response,*args,**kw)
        return wapper

class Header(Request):
    def __init__(self, url='',headers = {}):
        self.headers = headers
    def __call__(self,func):
        def wapper(*args, **kw):
            response = requests.request(method="HEADER",url=self.url, params=self.url)
            func(response,*args,**kw)
        return wapper

if __name__ == '__main__':
    @Get("https://www.bing.com")
    def handler(response:Optional[Response] = None):
        if(response != None):
            logger.debug("Httpx.js",response.status_code)
    handler()
    @Request(method="GET",url="https://www.bing.com")
    def handlerbing(response:Optional[Response] = None):
        if response != None:
            logger.info(response.content.decode())
    handlerbing()