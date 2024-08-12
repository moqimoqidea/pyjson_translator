import logging

# 创建一个自定义的 logger
pyjson_translator_logging = logging.getLogger('pyjson_translator')
pyjson_translator_logging.setLevel(logging.INFO)  # 默认日志级别设为 INFO

# 创建一个控制台处理器并设置默认的日志级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 默认日志级别设为 INFO

# 创建一个格式化器并将其设置到处理器上
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 将处理器添加到 logger 上
pyjson_translator_logging.addHandler(console_handler)


def set_logging_level(level):
    """
    设置 pyjson_translator 包的日志级别。

    :param level: 日志级别 (例如 logging.DEBUG, logging.INFO)
    """
    pyjson_translator_logging.setLevel(level)
    console_handler.setLevel(level)
