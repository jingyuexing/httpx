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
```
