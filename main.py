from flask import Flask, request, jsonify
import os, json, time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/fbfollow', methods=['GET'])
def fb_follow():
    follower = request.args.get("follower")
    amount = int(request.args.get("amount", 1))
    
    if not follower:
        return jsonify({"error": "Missing follower link"}), 400
    
    results = []

    # একাউন্ট ফাইলগুলো নির্বাচন
    files = [f for f in os.listdir() if f.endswith(".json")][:amount]

    for file in files:
        with open(file, "r") as f:
            cookies = json.load(f)
        status = follow_user(follower, cookies)
        results.append({ "account": file, "status": status })

    return jsonify({ "success": True, "results": results })

def follow_user(target_url, cookies):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)
        driver.get("https://www.facebook.com")
        time.sleep(2)

        # Add cookies one by one
        for cookie in cookies:
            cookie.pop("hostOnly", None)
            cookie["secure"] = True
            cookie["httpOnly"] = True
            cookie["sameSite"] = 'Lax'
            driver.add_cookie(cookie)

        # Refresh page after adding cookies
        driver.get(target_url)
        time.sleep(5)

        try:
            follow_button = driver.find_element("xpath", "//div[@aria-label='Follow']")
            follow_button.click()
            time.sleep(2)
            driver.quit()
            return "Followed successfully"
        except:
            driver.quit()
            return "Follow button not found"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
