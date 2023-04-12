"""
Crawler implementation
"""
from typing import Pattern, Union
from pathlib import Path
import json
import re
# import datetime
import requests
from bs4 import BeautifulSoup
from core_utils.config_dto import ConfigDTO
from core_utils.article.article import Article
from core_utils.constants import (TIMEOUT_LOWER_LIMIT,
                                  TIMEOUT_UPPER_LIMIT, NUM_ARTICLES_UPPER_LIMIT)
import shutil
from urllib.error import HTTPError, URLError


class IncorrectSeedURLError(Exception):
    """
    Raises when seed URL does not match standard pattern "https?://w?w?w?.
    """
    pass


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Raises when total number of articles is out of range from 1 to 150
    """
    pass


class IncorrectNumberOfArticlesError(Exception):
    """
    Raises when total number of articles to parse is not integer
    """
    pass


class IncorrectHeadersError(Exception):
    """
    Raises when total number of articles to parse is not integer
    """
    pass


class IncorrectEncodingError(Exception):
    """
    Raises when encoding does not specified as a string
    """
    pass


class IncorrectTimeoutError(Exception):
    """
    Raises when timeout value is not a positive integer less than 60
    """
    pass


class IncorrectVerifyError(Exception):
    """
    Raises when verify certificate value does not match bool value either True or False
    """
    pass


class IncorrectHeadlessError(Exception):
    """
    Raises when headless mode validation value does not match bool value either True or False
    """
    pass


class WebsiteError(Exception):
    """
    Raises when couldn't take a respond from Webpage
    """
    pass


class Config:
    """
    Unpacks and validates configurations
    """
    def __init__(self, path_to_config: Path) -> None:
        """
        Initializes an instance of the Config class
        """
        self.path_to_config = path_to_config
        self._validate_config_content()
        self._config_dto = self._extract_config_content()
        self._seed_urls = self._config_dto.seed_urls
        self._num_articles = self._config_dto.total_articles_to_find_and_parse
        self._headers = self._config_dto.headers
        self._encoding = self._config_dto.encoding
        self._timeout = self._config_dto.timeout
        self._verify_certificate = self._config_dto.should_verify_certificate
        self._headless_mode = self._config_dto.headless_mode

    def _extract_config_content(self) -> ConfigDTO:
        """
        Returns config values
        """
        with open(self.path_to_config, 'r', encoding='utf-8') as f:
            content = json.load(f)
        return ConfigDTO(**content)

    def _validate_config_content(self) -> None:
        """
        Ensure configuration parameters
        are not corrupt
        """

        if not isinstance(self._config_dto.seed_urls, list)\
                or not not all(isinstance(url, str) for url in self._config_dto.seed_urls)\
                or not all(re.match('https?://w?w?w?.', url) for url in self._config_dto.seed_urls)\
                or len(self._config_dto.seed_urls) == 0:
            raise IncorrectSeedURLError

        if not isinstance(self._config_dto.headers, dict):
            raise IncorrectHeadersError

        if not isinstance(self._config_dto.encoding, str):
            raise IncorrectEncodingError

        if not isinstance(self._config_dto.should_verify_certificate, int):
            raise IncorrectNumberOfArticlesError

        if self._config_dto.should_verify_certificate not in range(1, NUM_ARTICLES_UPPER_LIMIT + 1):
            raise NumberOfArticlesOutOfRangeError

        if not isinstance(self._config_dto.timeout, int) or self._config_dto.timeout \
                not in range(TIMEOUT_LOWER_LIMIT, TIMEOUT_UPPER_LIMIT + 1):
            raise IncorrectTimeoutError

        if not isinstance(self._config_dto.should_verify_certificate, bool):
            raise IncorrectVerifyError

        if not isinstance(self._config_dto.headless_mode, bool):
            raise IncorrectHeadlessError

    def get_seed_urls(self) -> list[str]:
        """
        Retrieve seed urls
        """
        return self._seed_urls

    def get_num_articles(self) -> int:
        """
        Retrieve total number of articles to scrape
        """
        return self._num_articles

    def get_headers(self) -> dict[str, str]:
        """
        Retrieve headers to use during requesting
        """
        return self._headers

    def get_encoding(self) -> str:
        """
        Retrieve encoding to use during parsing
        """
        return self._encoding

    def get_timeout(self) -> int:
        """
        Retrieve number of seconds to wait for response
        """
        return self._timeout

    def get_verify_certificate(self) -> bool:
        """
        Retrieve whether to verify certificate
        """
        return self._verify_certificate

    def get_headless_mode(self) -> bool:
        """
        Retrieve whether to use headless mode
        """
        return self._headless_mode


def make_request(url: str, config: Config) -> requests.models.Response:
    """
    Delivers a response from a request
    with given configuration
    """
    response = requests.get(url, headers=config.get_headers(), timeout=config.get_timeout(),
                            verify=config.get_verify_certificate())
    response.encoding = config.get_encoding()
    return response


class Crawler:
    """
    Crawler implementation
    """

    url_pattern: Union[Pattern, str]

    def __init__(self, config: Config) -> None:
        """
        Initializes an instance of the Crawler class
        """
        self.config = config
        self.urls = []
        self._seed_urls = config.get_seed_urls()

    def _extract_url(self, article_bs: BeautifulSoup) -> str:
        """
        Finds and retrieves URL from HTML
        """
        all_links_bs = article_bs.find_all('a')
        for links_bs in all_links_bs:
            link = links_bs.get('href')
        # link = article_bs.get('href')
            if link is not None and link.count('/') == 6 and '/cat/politroom/' in link and link[:8] == 'https://':
                self.urls.append(link)
        return ''

    def find_articles(self) -> None:
        """
        Finds articles
        """
        for seed_url in self._seed_urls:
            try:
                response = make_request(seed_url, self.config)
                main_bs = BeautifulSoup(response.text, 'lxml')
                self._extract_url(main_bs)
            except WebsiteError:
                continue

    def get_search_urls(self) -> list:
        """
        Returns seed_urls param
        """
        return self._seed_urls


class HTMLParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int, config: Config) -> None:
        """
        Initializes an instance of the HTMLParser class
        """
        pass

    def _fill_article_with_text(self, article_soup: BeautifulSoup) -> None:
        """
        Finds text of article
        """
        pass

    def _fill_article_with_meta_information(self, article_soup: BeautifulSoup) -> None:
        """
        Finds meta information of article
        """
        pass

    def unify_date_format(self, date_str: str) -> datetime.datetime:
        """
        Unifies date format
        """
        pass

    def parse(self) -> Union[Article, bool, list]:
        """
        Parses each article
        """
        pass


def prepare_environment(base_path: Union[Path, str]) -> None:
    """
    Creates ASSETS_PATH folder if no created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(parents=True, exist_ok=False)


def main() -> None:
    """
    Entrypoint for scrapper module
    """
    pass


if __name__ == "__main__":
    main()
