import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from .base_fetcher import BaseFetcher

class GithubScraper(BaseFetcher):
    def __init__(self, owner, repo, timeout=15):
        super().__init__(owner, repo)
        self.url = f"https://github.com/{owner}/{repo}"
        self.timeout = timeout
        self.wait_locator = (By.ID, "repo-stars-counter-star")

    def _initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service =  Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _convert_count(self, count_str):
        if not count_str or count_str == '0':
            return '0'

        count_str = count_str.replace(',', '').strip().lower()

        if count_str.endswith('k'):
            return str(int(float(count_str[:-1]) * 1000))
        elif count_str.endswith('m'):
            return str(int(float(count_str[:-1]) * 1000000))
        else:
            return count_str

    def _get_fork_count(self, driver):
        try:
            wait = WebDriverWait(driver, self.timeout)
            fork_element = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href$="/forks"] strong'))
            )
            return self._convert_count(fork_element.text)
        except Exception:
            return '0'

    def _parse_html(self, html_content, driver):
        soup = BeautifulSoup(html_content, 'html.parser')

        language_heading = soup.find("h2", string="Languages")
        language_element = language_heading.find_next("ul").find("span") if language_heading else None
        language = language_element.text.strip() if language_element else 'N/A'

        star_count_element = soup.find(id="repo-stars-counter-star")
        stars = self._convert_count(star_count_element['title']) if star_count_element and star_count_element.get('title') else '0'

        forks = self._get_fork_count(driver)

        return {
            "repository": f"{self.owner}/{self.repo}",
            "language": language,
            "stars": f"{int(stars):,}",
            "forks": f"{int(forks):,}"
        }

    def fetch(self):
        return self.scrape()

    def scrape(self):
        try:
            with self._initialize_driver() as driver:
                driver.get(self.url)
                wait = WebDriverWait(driver, self.timeout)
                wait.until(EC.visibility_of_element_located(self.wait_locator))
                time.sleep(1)
                return self._parse_html(driver.page_source, driver)
        except Exception as e:
            print(f"[{self.repo}] Um erro ocorreu durante a análise da página: {e}")
            return self.get_error_result()
