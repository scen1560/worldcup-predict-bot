import requests
import os
from datetime import datetime, timedelta

# ====================== 設定 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@my_ball_predict_3034")
GROK_API_KEY = os.getenv("GROK_API_KEY")

# ====================== 球隊中文映射 ======================
team_name_map = {
    "Ivory Coast": "科特迪瓦", "Ecuador": "厄瓜多爾",
    "Netherlands": "荷蘭", "Japan": "日本",
    "Argentina": "阿根廷", "France": "法國",
    "Brazil": "巴西", "Germany": "德國",
    "Spain": "西班牙", "England": "英格蘭",
    "Unknown": "未知"
}

def translate_team_name(name):
    return team_name_map.get(name, name)

# ====================== 賽程 ======================
def get_today_worldcup_matches():
    print("🔄 抓取世界盃賽程...")
    url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        today = datetime.now().strftime("%Y-%m-%d")
        matches = []
        for m in data.get("matches", []):
            if m.get("date") == today:
                matches.append({"home": m.get("team1"), "away": m.get("team2")})
        return matches[:2] if matches else [{"home": "荷蘭", "away": "日本"}]
    except:
        return [{"home": "科特迪瓦", "away": "厄瓜多爾"}]

# ====================== 用 Grok 生成 8 大板塊 ======================
def generate_with_grok(home_en, away_en):
    home = translate_team_name(home_en)
    away = translate_team_name(away_en)
    
    prompt = f"""你是一位專業香港足球分析員，用香港足球術語（波膽、大細球、受讓、派彩快等）為以下世界盃比賽撰寫完整 8 大板塊預測。

比賽：{home} vs {away}

要求：
- 強調新人、傷停、最新戰意
- 淡化歷史往績
- 內容自然專業、像真人分析
- 格式清晰，用 **粗體** 標題
- 最後加入派彩快提示
- 總結要實用"""

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1200
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=40)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            print("✅ Grok 成功生成預測內容")
            return content
    except Exception as e:
        print(f"⚠️ Grok API 錯誤: {e}，使用後備模板")
    
    # 後備模板
    return f"⚽️ **【世界盃：{home} vs {away}】**\nGrok 暫時無法生成，使用後備分析。\n推薦：受讓 / 大細球 2.5"

# ====================== 發送 ======================
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("🎉 成功發送到 Telegram 頻道！")
    else:
        print("❌ 發送失敗:", response.text)

# ====================== 主程式 ======================
if __name__ == "__main__":
    print("🚀 世界盃預測工具啟動...")
    matches = get_today_worldcup_matches()
    
    for m in matches:
        print(f"📝 正在分析：{m['home']} vs {m['away']}")
        report = generate_with_grok(m["home"], m["away"])
        send_to_telegram(report)
        print(f"✅ 已處理：{translate_team_name(m['home'])} vs {translate_team_name(m['away'])}\n")
