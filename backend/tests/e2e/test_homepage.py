from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def test_homepage_login_form():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("http://127.0.0.1:5173")

        assert driver.find_element(By.ID, "login-form").is_displayed()

        username_input = driver.find_element(By.ID, "username")
        username_input.send_keys("test_user")

        assert username_input.get_attribute("value") == "test_user"

    finally:
        driver.quit()
