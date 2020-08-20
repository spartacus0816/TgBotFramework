# NoneBot.log 模块

## 日志

NoneBot 使用标准库 [logging](https://docs.python.org/3/library/logging.html) 来记录日志信息。

自定义 logger 请参考 [logging](https://docs.python.org/3/library/logging.html) 文档。


## `logger`


* **说明**

    NoneBot 日志记录器对象。



* **默认信息**

    
    * 格式: `[%(asctime)s %(name)s] %(levelname)s: %(message)s`


    * 等级: `DEBUG` / `INFO` ，根据 config 配置改变


    * 输出: 输出至 stdout



* **用法**


```python
from nonebot.log import logger

# 也可以这样
import logging
logger = logging.getLogger("nonebot")
```
