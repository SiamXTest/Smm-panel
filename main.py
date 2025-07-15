from flask import Flask, request, jsonify
import os, json, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

app = Flask(__name__)
ACCOUNTS_DIR = "fb_accounts"

@app.route("/fbfollow", methods=["GET"])
def fbfollow():
    follower = request.args.get("follower")
    amount = int(request.args.get("amount", 1))

    if not follower:
        return jsonify({"error": "Missing follower link"}), 400

    files = os.listdir(ACCOUNTS_DIR)[:amount]
    results = []

    for filename in files:
        path = os.path.join(ACCOUNTS_DIR, filename)
        with open(path) as f:
            acc = json.load(f)
        status = follow_user(follower, acc["cookie"], acc["useragent"])
        results.append({ "account": filename, "status": status })

    return jsonify({"success": True, "results": results})

def follow_user(target_link, cookie_str, useragent):
    try:
        options = uc.ChromeOptions()
        options.add_argument(f'user-agent={useragent}')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = uc.Chrome(options=options)

        # Add cookies
        driver.get("https://facebook.com")
        driver.delete_all_cookies()
        for item in cookie_str.split(";"):
            name, value = item.strip().split("=", 1)
            driver.add_cookie({"name": name, "value": value, "domain": ".facebook.com"})

        driver.get(target_link)
        time.sleep(3)

        try:
            btn = driver.find_element("xpath", "//div[@aria-label='Follow']")
            btn.click()
            time.sleep(2)
            driver.quit()
            return "Followed"
        except:
            driver.quit()
            return "Follow button not found"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
