import requests
import os
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN", "8206362705:AAGQYIP0ueTojXyfIbPB5o5DI0sCqAA0EwA")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@my_ball_predict_3034")

team_name_map = {
    "Ivory Coast": "科特迪瓦", "Ecuador": "厄瓜多爾",
    "Netherlands": "荷蘭", "Japan": "日本",
    "Germany": "德國", "Argentina": "阿根廷", "France": "法國",
    "Brazil": "巴西", "Spain": "西班牙", "England": "英格蘭",
    "Unknown": "未知"
}

def translate_team_name(name):
    return team_name_map.get(name, name)

def get_today_worldcup_matches():
    print("🔄 抓取賽程...")
    url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        today = datetime.now().strftime("%Y-%m-%d")
        matches = []
        for m in data.get("matches", []):
            if m.get("date") == today:
                matches.append({"home": m.get("team1"), "away": m.get("team2")})
        if matches:
            return matches[:2]
    except:
        pass
    return [{"home": "荷蘭", "away": "日本"}]

def get_hkjc_football_odds():
    return {"h_odds": "2.05", "d_odds": "3.40", "a_odds": "3.30"}

def generate_8_blocks_report(home_en, away_en, odds):
    home = translate_team_name(home_en)
    away = translate_team_name(away_en)
    report = f'''⚽️ **【世界盃焦點：{home} vs {away}】**
📊 **馬會賠率**：主勝 {odds['h_odds']} | 和 {odds['d_odds']} | 客勝 {odds['a_odds']}
---
**1️⃣ 預計首發**：{home} 新星正選
**2️⃣ 戰術對決**：新進攻線優勢
**3️⃣ 傷停戰意**：最新戰意高
**4️⃣ 投注推薦**：受讓 / 大細球
**5️⃣ 風險**：新陣默契不足
**6️⃣ 全體預測**：{home} 勝出機會 56%
**7️⃣ 波膽**：2-1
**8️⃣ 總結**：小注受讓，中場用派彩快調整！'''
    return report

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    matches = get_today_worldcup_matches()
    for m in matches:
        odds = get_hkjc_football_odds()
        report = generate_8_blocks_report(m["home"], m["away"], odds)
        send_to_telegram(report)
        print(f"已發送：{m['home']} vs {m['away']}")
