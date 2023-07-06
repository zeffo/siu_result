from typing import Any, Awaitable, TypeVar
import aiohttp
import yarl
from playwright.async_api import (
    Browser,
    BrowserType,
    Page,
    Playwright,
    Response,
    TimeoutError,
)


__all__ = ("Scraper",)


T = TypeVar("T")


async def retry(
    coro: Awaitable[T], *, exceptions: list[type[BaseException]], action: Awaitable[Any]
) -> T:
    while True:
        try:
            res = await coro
        except* exceptions:
            await action
        else:
            return res


class NoBrowserException(RuntimeError):
    """Raised when the Scraper's internal Browser was closed unexpectedly.
    Please ensure that the Scraper is used as an async context manager."""


class Scraper:
    """Represents a Scraper for obtaining SIU exam results.

    Parameters
    ----------
    browser_type: :class:`playwright.BrowserType`
        The type of browser to use.

    """

    BASE = "http://siuexam.siu.edu.in/forms/resultview.html"
    SEAT_XPATH = (
        r"xpath=//html/body/div[2]/form/div/div[1]/div[2]/div/div/div/div/div/input[1]"
    )
    VIEW_XPATH = (
        r"xpath=//html/body/div[2]/form/div/div[1]/div[2]/div/div/div/div/div/input[2]"
    )
    LOGIN_INPUT_ID = "#login"
    LOGIN_BTN_ID = "#lgnbtn"
    RESULT_BTN_XPATH = "xpath=//html/body/div[2]/form/div/div[2]/div[1]/a"

    def __init__(self, playwright: Playwright, browser_type: BrowserType):
        self.browser_type = browser_type
        self.pw: Playwright = playwright
        self._browser: Browser | None = None

    async def __aenter__(self):
        self._browser = await self.browser_type.launch()
        return self

    async def __aexit__(self, *_):
        if self._browser:
            await self._browser.close()

    @property
    def browser(self) -> Browser:
        if b := self._browser:
            return b
        raise NoBrowserException

    async def force_load(self, url: str, *, timeout: float | None = 0) -> Page:
        """Attempts to open a URL till it successfully loads."""
        page = await self.browser.new_page()
        resp: Response | None = None
        while not resp or resp.status != 200:
            resp = await page.goto(url, timeout=timeout)
        return page

    async def run(self, prn: str, seat_no: str, output: str) -> None:
        page = await self.force_load(self.BASE)
        await page.locator(self.LOGIN_INPUT_ID).fill(prn)
        await page.locator(self.LOGIN_BTN_ID).click()
        await page.locator(self.SEAT_XPATH).fill(seat_no)
        res_loc = page.locator(self.VIEW_XPATH)
        click_res = res_loc.click()
        await click_res

        src = await retry(
            page.locator(self.RESULT_BTN_XPATH).get_attribute("href", timeout=50),
            exceptions=[TimeoutError],
            action=click_res,
        )

        url = yarl.URL(self.BASE)
        target = url.join(yarl.URL(str(src)))

        resp = None
        async with aiohttp.ClientSession() as session:
            while not resp or resp.status != 200:
                resp = await session.get(target)
            with open(output, "wb") as f:
                f.write(await resp.content.read())
