from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time


class _selenium():
    def chrome_driver(self, user_agent="", headless=True, dl_path=""):
        """
        Start a local Google Chrome driver using selenium.
        For a fresh and easy install, the diver is handled by webdriver_manager.chrome.ChromeDriverManager.
        :param user_agent: string: set a specific user agent you wish to use for the driver.
        :param headless: boolean: True makes the driver headless.
        :param dl_path: string: Set a specific path for files to be downloaded when using the driver.
        :return: object: The chrome driver object is returned. It is typically handed to a variable for further usage.
        """
        options = webdriver.ChromeOptions()

        if not user_agent:
            user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"""

        if headless:
            options.add_argument('--headless')

        options.add_argument('user-agent={}'.format(user_agent))
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        # options.add_argument('--single-process') # This causes issues

        # Experimental preferences.
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        if dl_path:
            prefs = {'download.default_directory': dl_path}
            options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(ChromeDriverManager().install(), options=options)

    def remote_selenium_driver(self, hub_ip_port="192.168.152.162:4444", browser="chrome", user_agent="", headless=True, sleep=0, dl_path=""):
        """
        Start a local Google Chrome driver using selenium. This is only for usage with Selenium Grid.
        :param hub_ip_port: string: The IP and Port of the Selenium Grid Hub. Example: 192.168.152.162:4444
        :param browser: string: The browser you wish to use. Currently, only Chrome is supported.
        :param user_agent: string: set a specific user agent you wish to use for the driver.
        :param headless: boolean: True makes the driver headless.
        :param sleep: int: Optional time to sleep when starting the driver.
        :param dl_path: string: Set a specific path for files to be downloaded when using the driver. This is the path on the remote node being used, plan accordingly.
        :return: object: The chrome driver object is returned. It is typically handed to a variable for further usage.
        """
        if not user_agent:
            user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"""

        time.sleep(int(sleep))

        options = webdriver.ChromeOptions()
        options.add_argument("user-agent={}".format(user_agent))

        if headless:
            options.add_argument("--headless")

        if dl_path:
            p = {'download.default_directory': dl_path}
            options.add_experimental_option("prefs", p)

        #driver = webdriver.Remote(command_executor='http://{}/wd/hub'.format(hub_ip_port), desired_capabilities={'browserName': browser, 'javascriptEnabled': True}, options=options)

        return webdriver.Remote(command_executor='http://{}/wd/hub'.format(hub_ip_port), desired_capabilities={'browserName': browser, 'javascriptEnabled': True}, options=options)

    def beta_chrome_driver(self, user_agent="", headless=True, dl_path="", proxy={}):
        """
        Trying to get proxy working. Don't use this yet.
        :param user_agent:
        :param headless:
        :param dl_path:
        :param proxy:
        :return:
        """
        options = webdriver.ChromeOptions()

        if not user_agent:
            user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"""

        if headless:
            options.add_argument('--headless')
        #
        if proxy:
            print(proxy)
            if proxy['connection'].upper() == 'SOCKS4':
                options.add_argument('--proxy-server=socks4://{}:{}'.format(proxy['ip'], proxy['port']))
            elif proxy['connection'].upper() == 'SOCKS5':
                options.add_argument('--proxy-server=socks5://{}:{}'.format(proxy['ip'], proxy['port']))
            else:
                options.add_argument('--proxy-server=ipaddress:port')

        options.add_argument('user-agent={}'.format(user_agent))
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        # options.add_argument('--single-process') # This causes issues

        # Experimental preferences.
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        if dl_path:
            prefs = {'download.default_directory': dl_path}
            options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(ChromeDriverManager().install(), options=options)

class acts():
    def scroll_to_bottom(self, driver):
        """
        Makes the driver scroll to the bottom of the page.
        :param driver: object: Selenium driver.
        :return: object: Selenium driver.
        """
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        return driver

    def scroll_to_top(self, driver):
        """
        Makes the driver scroll to the top of the page.
        :param driver: object: Selenium driver.
        :return: object: Selenium driver.
        """
        driver.execute_script("window.scrollTo(document.body.scrollHeight,0)")
        return driver

    def scroll_down_loop(self, driver, multiples=50, sleep_time=.1):
        """
        Makes the driver scroll to the bottom of the page in a controlled pace.
        :param driver: object: Selenium driver.
        :param multiples: int: Scroll the entire length in multiples. Page length / multiples = size of single scroll.
        :param sleep_time: int: Sleep between each scroll down.
        :return: object: Selenium driver.
        """
        page_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        value = int(page_height / multiples)
        page_breaks = [[i * value, (i + 1) * value] for i in range(0, multiples)]
        page_breaks[-1][-1] = page_height
        for height in page_breaks:
            driver.execute_script("window.scrollTo({},{})".format(height[0], height[1]))
            time.sleep(sleep_time)
        return driver

    def window_to_page_size(self, driver, atleast_1920=True):
        """
        Reshape window size to page size.
        :param driver: object: Selenium driver.
        :param atleast_1920: If the page is smaller than 1920x1080, use 1920 length or 1080 width (done separately).
        :return: object: Selenium driver.
        """
        total_width = driver.execute_script("return document.body.offsetWidth")
        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        if atleast_1920:
            if total_width < 1920:
                total_width = 1920
            if total_height < 1080:
                total_height = 1080
        driver.set_window_size(total_width, total_height)
        return driver

def main():
    pass

if __name__ == '__main__':
    main()