# -*- coding: utf-8 -*-
# @Author: admin
# @Date:   2022-04-17 13:58:03
# @Last Modified by:   admin
# @Last Modified time: 2022-04-17 18:07:08

from io import BufferedReader
from typing import Callable, Dict,Any, Literal, Optional, Union,Generic,TypeVar
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
    async def __call__(self,func):
        def wapper(*args, **kw):
           return func(*args,**kw)
        return wapper

class Cookies:
    """docstring for Cookies"""
    cookie = ""
    query = {}

    def __init__(self, cookies=''):
        self.parserCookies(cookies=cookies)
        self.cookie = self.__str__()

    def setCookies(self, key, value):
        self.query[key] = value
        self.cookie = self.__str__()

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
    def toJSON(self):
        return json.dumps(self.query,ensure_ascii=False)

    def replaceCookies(self, old='', new=''):
        oldCookies = Cookies(old)
        newCookies = Cookies(new)
        for key in dict.keys(newCookies.query):
            oldCookies.setCookies(key, newCookies.getCookies(key))
        return oldCookies.__str__()

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
    headers:Optional[Dict[str,str]]
    method:str
    stream:bool = False
    file:Optional[BufferedReader] = None
    json:Optional[Union['BaseModel',Dict[str,Any]]] = None
    form:Optional[Dict[str,Any]] = None
    path:Optional[Dict[str,Any]] = None
    query:Optional[Dict[str,Any]] = None
    verify:Optional[Any] = None
    def __init__(self,
        method:str,
        url:str,
        query:Optional[Dict[str,Any]]=None,
        path:Optional[Dict[str,Any]]=None,
        file:Optional[str] = None,
        cookie:Optional[Dict[str,Any]]=None,
        header:Optional[Dict[str,Any]]=None,
        auth:Optional[Any]=None,
        json:Optional[Union['BaseModel',Dict[str,Any]]] = None,
        form:Optional[Dict[str,Any]]=None,
        verify:Optional[Any] = None
    ) -> None:
        self.method = method
        self.url = url
        self.auth = auth
        self.query = query
        self.path = path
        self.json = json
        self.form = form
        self.verify = verify
        self.file = self.readFile(file)
        self.headers = header
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
    def formatURLPath(self,url:str,data:Optional[Dict[str,Any]]= None):
        if(data != None):
            backupURL = url
            for key in data:
                backupURL = backupURL.replace("{%s}"%(key),str(data.get(key)),1)
                backupURL = backupURL.replace(":%s"%(key),str(data.get(key)),1)
            return backupURL
        return url
    def readFile(self,file:Optional[str] = None):
        if file != None:
            with open(file=file,mode='rb') as file_:
                return file_
    def merge(self,old:Optional[Dict[str,Any]] = None,newDict:Optional[Dict[str,Any]] = None):
        if(not old and newDict):
            return newDict
        elif(old and not newDict):
            return old
        elif(not old and not newDict):
            return {}
        elif(old and newDict):
            return old.update(newDict)
    def __call__(self, func) -> Any:
        def wapper(*args,**kw):
            self.method = kw.get("method") or self.method
            self.url = kw.get("url") or self.url
            self.cookies = self.parseCookie(kw.get('cookies'))
            self.path = self.merge(self.path,kw.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kw.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kw.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kw.get('json'))
            else:
                self.json =  self.merge(self.json,kw.get('json'))

            self.auth = self.merge(self.auth,kw.get("auth"))
            self.verify = kw.get("verify") or self.verify
            self.file = self.readFile(kw.get('file')) or self.file
            response = requests.request(
                method=self.method.upper(),
                url=self.formatURLPath(self.url,self.path),
                params=self.query,
                headers=self.headers,
                cookies=self.cookies,
                json=self.json,
                data=self.form,
                verify=self.verify,
                stream= self.stream
            )
            return func(response,*args,**kw)
        return wapper

class Get(Request):
    cookies:Optional['RequestsCookieJar'] = None
    auth:Optional[Any]
    headers:Optional[Dict[str,str]]
    method:str
    stream:bool = False
    file:Optional[BufferedReader] = None
    json:Optional[Union['BaseModel',Dict[str,Any]]] = None
    form:Optional[Dict[str,Any]]
    path:Optional[Dict[str,Any]]
    query:Optional[Dict[str,Any]]
    verify:Optional[Any] = None
    def __init__(
        self,
        url:str,
        query:Optional[Dict[str,Any]]=None,
        path:Optional[Dict[str,Any]]=None,
        file:Optional[str] = None,
        cookie:Optional[Dict[str,Any]]=None,
        header:Optional[Dict[str,Any]]=None,
        auth:Optional[Any]=None,
        json:Optional[Union['BaseModel',Dict[str,Any]]] = None,
        form:Optional[Dict[str,Any]]=None,
        verify:Optional[Any] = None
    ):
        self.url = url
        self.query = query
        self.path = path
        self.auth = auth
        self.file = self.readFile(file)
        self.cookies = self.parseCookie(cookie)
        self.json = json
        self.headers = header
        self.form  = form
        self.verify = verify
        self.parsePath(self.path)
    def __call__(self, func:Callable):
        def wrapper(*args, **kwargs):
            self.method = kwargs.get("method") or self.method
            self.url = kwargs.get("url") or self.url
            self.cookies = self.parseCookie(kwargs.get('cookies'))
            self.path = self.merge(self.path,kwargs.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kwargs.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kwargs.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kwargs.get('json'))
            else:
                self.json =  self.merge(self.json,kwargs.get('json'))

            self.auth = kwargs.get("auth") or self.auth
            self.verify = kwargs.get("verify") or self.verify
            self.file = self.readFile(kwargs.get('file')) or self.file
            response = requests.get(
                url=self.formatURLPath(self.url,self.path),
                params=self.query,
                data=self.form,
                headers=self.headers,
                auth=self.auth,
                verify= self.verify
            )
            return func(response, *args, **kwargs)
        return wrapper

class Post(Request):
    def __init__(self, 
        url,
        file:Optional[str]=None,
        path:Optional[Dict[str,Any]]=None,
        query:Optional[Dict[str,Any]]=None,
        json:Optional['BaseModel']=None,
        auth:Optional[Any]=None,
        form:Optional[Any] = None,
        cookies:Optional[Union[Dict[str,Any],str]] = None
    ):
        self.url = url
        self.path = path
        self.query = query
        self.json = json
        self.auth = auth
        self.form = form
        self.file = self.readFile(file)
        self.cookies = self.parseCookie(cookies=cookies)
        self.parsePath(self.path)
    def __call__(self,func):
        def wapper(*args, **kw):
            self.method = kw.get("method") or self.method
            self.url = kw.get("url") or self.url
            self.cookies = self.parseCookie(kw.get('cookies'))
            self.path = self.merge(self.path,kw.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kw.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kw.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kw.get('json'))
            else:
                self.json =  self.merge(self.json,kw.get('json'))

            self.auth = kw.get("auth") or self.auth
            self.verify = kw.get("verify") or self.verify
            self.file = self.readFile(kw.get('file')) or self.file
            response = requests.post(
                url=self.formatURLPath(self.url,self.path),
                json=self.json,
                params=self.query,
                auth=self.auth,
                data=self.form, 
                cookies=self.cookies,
                headers=self.headers
            )
            return func(response, *args, **kw)
        return wapper

class Put(Request):
    def __init__(
        self,
        url:str,
        file:Optional[str]=None,
        path:Optional[Dict[str,Any]]=None,
        query:Optional[Dict[str,Any]]=None,
        json:Optional['BaseModel']=None,
        auth:Optional[Any]=None,
        form:Optional[Any] = None,
        cookies:Optional[Union[Dict[str,Any],str]] = None
    ):
        self.url = url
        self.path = path
        self.json = json
        self.form = form
        self.auth = auth
        self.query = query
        self.file = self.readFile(file=file)
        self.path = self.path
        self.cookies = self.parseCookie(cookies=cookies)
    def __call__(self,func):
        def wapper(*args, **kw):
            self.method = kw.get("method") or self.method
            self.url = kw.get("url") or self.url
            self.cookies = self.parseCookie(kw.get('cookies'))
            self.path = self.merge(self.path,kw.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kw.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kw.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kw.get('json'))
            else:
                self.json =  self.merge(self.json,kw.get('json'))

            self.auth = kw.get("auth") or self.auth
            self.verify = kw.get("verify") or self.verify
            self.file = self.readFile(kw.get('file')) or self.file
            response = requests.request(
                method="PUT",
                url=self.formatURLPath(self.url,self.path),
                params=self.query,
                json=self.json,
                cookies=self.cookies,
                headers= self.headers,
                auth=self.auth,
                data=self.form
            )
            return func(response,*args,**kw)
        return wapper

class Options(Request):
    def __init__(
        self,
        url:str,
        file:Optional[str]=None,
        path:Optional[Dict[str,Any]]=None,
        query:Optional[Dict[str,Any]]=None,
        json:Optional['BaseModel']=None,
        auth:Optional[Any]=None,
        headers:Optional[Dict[str,Any]]=None,
        form:Optional[Any] = None,
        cookies:Optional[Union[Dict[str,Any],str]] = None
    ):
        self.url = url
        self.path = path
        self.json = json
        self.form = form
        self.auth = auth
        self.query = query
        self.file = self.readFile(file=file)
        self.path = self.path
        self.headers = headers
        self.cookies = self.parseCookie(cookies=cookies)
    def __call__(self,func):
        def wapper(*args, **kw):
            self.method = kw.get("method") or self.method
            self.url = kw.get("url") or self.url
            self.cookies = self.parseCookie(kw.get('cookies'))
            self.path = self.merge(self.path,kw.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kw.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kw.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kw.get('json'))
            else:
                self.json =  self.merge(self.json,kw.get('json'))

            self.auth = kw.get("auth") or self.auth
            self.verify = kw.get("verify") or self.verify
            self.file = self.readFile(kw.get('file')) or self.file
            response = requests.request(
                method="OPTIONS",
                url=self.formatURLPath(self.url,self.path),
                params=self.query,
                json=self.json,
                cookies=self.cookies,
                headers= self.headers,
                auth=self.auth,
                data=self.form
            )
            return func(response,*args,**kw)
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
            self.method = kw.get("method") or self.method
            self.url = kw.get("url") or self.url
            self.cookies = self.parseCookie(kw.get('cookies'))
            self.path = self.merge(self.path,kw.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kw.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kw.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kw.get('json'))
            else:
                self.json =  self.merge(self.json,kw.get('json'))

            self.auth = kw.get("auth") or self.auth
            self.verify = kw.get("verify") or self.verify
            self.file = self.readFile(kw.get('file')) or self.file
            response = requests.request(
                method="PATCH",
                url=self.url,
                params=self.query,
                cookies=self.cookies,
                headers=self.headers,
                json=self.json,
                data=self.form,
                auth=self.auth,
            )
            return func(response,*args,**kw)
        return wapper

class Delete(Request):
    def __init__(self, 
        url:str,
        file:Optional[str]=None,
        path:Optional[Dict[str,Any]]=None,
        query:Optional[Dict[str,Any]]=None,
        json:Optional['BaseModel']=None,
        auth:Optional[Any]=None,
        form:Optional[Any] = None,
        cookies:Optional[Union[Dict[str,Any],str]] = None
    ):
        self.url = url
        self.path = path
        self.query = query
        self.json = json
        self.auth = auth
        self.form = form
        self.cookies = self.parseCookie(cookies=cookies)
        self.parsePath(self.path)
        self.file = self.readFile(file=file)
    def __call__(self,func):
        def wapper(*args, **kw):
            self.method = kw.get("method") or self.method
            self.url = kw.get("url") or self.url
            self.cookies = self.parseCookie(kw.get('cookies'))
            self.path = self.merge(self.path,kw.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kw.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kw.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kw.get('json'))
            else:
                self.json =  self.merge(self.json,kw.get('json'))

            self.auth = kw.get("auth") or self.auth
            self.verify = kw.get("verify") or self.verify
            self.file = self.readFile(kw.get('file')) or self.file
            response = requests.request(
                method="DELETE",
                url=self.formatURLPath(self.url,self.path),
                params=self.url,
                data=self.form,
                json=self.json,
                cookies=self.cookies,
                auth=self.auth,
                verify=self.verify
            )
            return func(response,*args,**kw)
        return wapper

class Header(Request):
    def __init__(
        self,
        url:str='',
        query:Optional[Dict[str,Any]]=None,
        path:Optional[Dict[str,Any]]=None,
        cookie:Optional[Dict[str,Any]] = None,
        json:Optional[Union[Dict[str,Any],'BaseModel']] = None,
        headers:Optional[Dict[str,Any]] = None,
        form:Optional[Dict[str,Any]] = None
    ):
        self.url = url
        self.cookies = self.parseCookie(cookies=cookie)
        self.json = json
        self.form = form
        self.headers = headers
        self.query = query
        self.path = path
    def __call__(self,func):
        def wapper(*args, **kw):
            self.method = kw.get("method") or self.method
            self.url = kw.get("url") or self.url
            self.cookies = self.parseCookie(kw.get('cookies'))
            self.path = self.merge(self.path,kw.get('path'))
            overrideHeaders:Optional[Dict[str,Any]] = kw.get("headers")
            if overrideHeaders:
                self.headers = self.headers or {}
                for key in overrideHeaders:
                    self.headers[key] = overrideHeaders[key]
            self.query = self.merge(self.query,kw.get("query"))
            if isinstance(self.json,BaseModel):
                self.json =  self.merge(self.json.dict(),kw.get('json'))
            else:
                self.json =  self.merge(self.json,kw.get('json'))

            self.auth = kw.get("auth") or self.auth
            self.verify = kw.get("verify") or self.verify
            self.file = self.readFile(kw.get('file')) or self.file
            response = requests.request(
                method="HEADER",
                url=self.formatURLPath(self.url,self.path),
                params=self.query,
                json=self.json,
                cookies=self.cookies,
                headers=self.headers,
                auth=self.auth
            )
            return func(response,*args,**kw)
        return wapper

if __name__ == '__main__':    
    @Get("http://localhost:8388/api/author/:uid")
    def handler(response:Optional[Response]=None,**kw):
        if response != None:
            logger.info(response.json())
            return response.json()
    
    @Request(method="GET",url="https://www.google.com")
    def process(response:Optional[Response] = None):
        if(response != None):
            return response.json()
        return ""
    
    @Options(url="https://api.bilibili.com/x/relation/stat")
    def getUserSpace(response:Optional[Response] = None,**kw):
        if(response != None):
            return response
    result = handler(
        path={
            "uid":20
        },
        query={
            "page":12,
            "size":10
        }
    )
    print(result)
    responseData = getUserSpace(
        query={
            "vmid":50660116     
        }
    )
    print(responseData)
