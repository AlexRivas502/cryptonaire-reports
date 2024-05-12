import logging
import structlog


class LoggerConfig:

    def __init__(self, log_level: str = "info") -> None:
        match log_level.lower():
            case "info":
                log_level = logging.INFO
            case "debug":
                log_level = logging.DEBUG
            case "warning":
                log_level = logging.WARNING
            case "error":
                log_level = logging.ERROR
            case _:
                raise KeyError()

        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(log_level)
        )
