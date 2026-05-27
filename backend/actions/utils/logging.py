"""
Structured logging setup using loguru.
Outputs JSON in production, coloured text in development.
"""

import os
import sys
from pathlib import Path

from loguru import logger


def setup_logging() -> None:
    """Configure loguru for the action server."""
    # Remove default handler
    logger.remove()

    is_production = os.getenv("ENV", "development") == "production"
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    if is_production:
        # JSON structured logs — parseable by Datadog, Loki, etc.
        logger.add(
            sys.stdout,
            format="{message}",
            level="INFO",
            serialize=True,  # outputs valid JSON lines
            enqueue=True,  # async-safe
        )
    else:
        # Human-readable with colour for local dev
        dev_format = (
            "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>"
        )
        logger.add(
            sys.stderr,
            format=dev_format,
            level="DEBUG",
            colorize=True,
        )

    # Error log file for post-mortem debugging (both dev and prod)
    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        rotation="10 MB",
        retention="7 days",
        serialize=is_production,
    )

    # Debug log file (dev only, can get large)
    if not is_production:
        logger.add(
            log_dir / "debug.log",
            level="DEBUG",
            rotation="5 MB",
            retention="3 days",
        )

    logger.debug("Logging initialized", env=os.getenv("ENV", "development"))
