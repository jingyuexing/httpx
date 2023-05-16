# HTTPX(Client)


# usage
```python
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


@Get("http://localhost:8388/api/author/:uid")
    def handler(response:Optional[Response]=None,**kw):
        if response != None:
            logger.info(response.json())
        return response.json()

    handler(
        path={
            "uid":20
        },
        query={
            "page":12,
            "size":10
        }
    )

data = handler()
```
