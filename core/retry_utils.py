"""
retry_utils.py — 共用的 retry + exponential backoff 工具

用途：為所有外部 API 呼叫提供統一的重試邏輯。
"""

import time
import logging

logger = logging.getLogger(__name__)


def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=30.0,
                       retryable_exceptions=(Exception,)):
    """
    執行 func()，失敗時以 exponential backoff 重試。

    :param func: 要執行的 callable（無參數，用 lambda 包裝）
    :param max_retries: 最大重試次數（不含首次執行）
    :param base_delay: 首次重試等待秒數
    :param max_delay: 最長等待秒數上限
    :param retryable_exceptions: 哪些例外類型會觸發重試
    :return: func() 的回傳值
    :raises: 最後一次失敗的例外
    """
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except retryable_exceptions as e:
            last_exception = e
            if attempt < max_retries:
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(
                    f"第 {attempt + 1} 次失敗: {e}，{delay:.1f} 秒後重試..."
                )
                time.sleep(delay)
            else:
                logger.error(f"已重試 {max_retries} 次仍失敗: {e}")
    raise last_exception
