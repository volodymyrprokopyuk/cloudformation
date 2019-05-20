"""Log and publish metrics to CloudWatch"""
from jsonlogging import with_logger


@with_logger(__name__)
def main(logger):
    """Log and publish metrics to CloudWatch"""
    logger.setLevel("DEBUG")

    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("fatal")


if __name__ == "__main__":
    main()
