from loguru import logger
logger.remove()
logger.add("kerchunking_{time}.log")#, compression="tar.gz")
