import playwright
from playwright.sync_api import sync_playwright
from PIL import Image
import os


def replace_html_content_placeholder(name, title):
    return """
    <!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Media Post</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Arial:wght@700&display=swap');
        body {
            font-family: Arial, sans-serif;
            background: transparent;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-weight: bold;
        }
        .post {
            background: white;
            width: 400px; /* Weniger Breite für kompakteres Design */
            padding: 18px; /* Geringeres Padding */
            border-radius: 12px;
            box-shadow: 0px 0px 25px rgba(0, 0, 0, 0.85); /* Dunklerer Schatten */
            font-size: 20px;
            position: relative;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 6px;
            position: relative;
        }
        .avatar img {
            width: 40px; /* Profilbild kleiner */
            height: 40px;
            border-radius: 50%;
        }
        .username-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-left: 6px;
        }
        .username {
            font-weight: bold;
            font-size: 16px; /* Kleiner für kompakteres Design */
            display: flex;
            margin-bottom: 5px;
            margin-top: -5px;
            align-items: center;
        }
        .verified img {
            width: 16px; /* Verifizierungs-Badge kleiner */
            height: 16px;
            margin-left: 3px;
        }
        .views {
            font-size: 11px; /* Kleiner für dezente Anzeige */
            color: gray;
            margin-top: -3px;
        }
        .content {
            font-size: 22px; /* Leicht reduziert */
            line-height: 1.2;
            margin-bottom: 6px;
        }
        .footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: gray;
            font-size: 16px; /* Kleiner für dezente Anzeige */
            position: relative;
        }
        .likes-comments {
            display: flex;
            align-items: center;
            margin-bottom: -13px;
        }
        .likes, .comments {
            display: flex;
            align-items: center;
            margin-right: 4px;
            font-size: 11px; /* Noch kompakter */
        }
        .likes {
            margin-right: 8px;
        }
        .share {
            position: absolute;
            right: 6px;
            bottom: 4px;
            font-size: 11px; /* Etwas kleiner */
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="post">
        <div class="header">
            <div class="avatar">
                <img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png" alt="Avatar"/>
            </div>
            <div class="username-container">
                <div class="username">@PLACEHOLDER_NAME
                    <div class="verified">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e4/Twitter_Verified_Badge.svg" alt="Verifiziert"/>
                    </div>
                </div>
                <div class="views">👁️ 731,924</div>
            </div>
        </div>
        <div class="content">
            PLACEHOLDER_BODY
        </div>
        <div class="footer">
            <div class="likes-comments">
                <div class="likes">❤️ 999+</div>
                <div class="comments">💬 999+</div>
            </div>
            <div class="share">🔗</div>
        </div>
    </div>
</body>
</html>
""".replace("PLACEHOLDER_NAME", name).replace("PLACEHOLDER_BODY", title)


def html_to_png(user_dir, html_content, output_file, width=550, height=800, scale_factor=1):
    temp_html_file = user_dir + "temp.html"
    with open(temp_html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": width * scale_factor, "height": height * scale_factor,
                      "device_scale_factor": scale_factor}
        )
        page.goto(f"file://{os.path.abspath(temp_html_file)}")
        page.screenshot(path=output_file, omit_background=True)
        browser.close()

    print(f"✅ Hochwertiger Screenshot gespeichert als {output_file}")

    os.remove(temp_html_file)
    return output_file
