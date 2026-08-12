from selenium import webdriver
from selenium.webdriver.common.by import By


def test_homepage_login_form():
    driver = webdriver.Chrome()

    try:
        driver.get("http://127.0.0.1:5173")

        assert driver.find_element(By.ID, "login-form").is_displayed()

        username_input = driver.find_element(By.ID, "username")
        username_input.send_keys("test_user")

        assert username_input.get_attribute("value") == "test_user"

    finally:
        driver.quit()
