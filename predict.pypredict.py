import requests
from datetime import datetime

# ====================== 設定（使用 Secret） ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003860795845"
GROK_API_KEY = os.getenv("GROK_API_KEY")

print("🚀 世界盃預測工具啟動...")
print("BOT_TOKEN:", "已載入" if BOT_TOKEN else "❌ 未載入")
print("GROK_API_KEY:", "已載入" if GROK_API_KEY else "❌ 未載入")

# ====================== 球隊映射 ======================
team_name_map = {
    "Germany": "德國", "Japan": "日本", "Curaçao": "庫拉索",
    "Ivory Coast": "科特迪瓦", "Ecuador": "厄瓜多爾",
    "Unknown": "未知"
}

def translate_team_name(name):
    return team_name_map.get(name, name)

# ====================== 自動抓賽程 ======================
def get_today_matches():
    print("🔄 抓取今日世界盃賽程...")
    try:
        url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
        data = requests.get(url, timeout=15).json()
        today = datetime.now().strftime("%Y-%m-%d")
        matches = []
        for m in data.get("matches", []):
            if m.get("date") == today:
                matches.append({"home": m.get("team1"), "away": m.get("team2")})
        return matches[:2] if matches else [{"home": "Germany", "away": "Curaçao"}]
    except:
        return [{"home": "Germany", "away": "Curaçao"}]

# ====================== Grok 生成 8 大板塊 ======================
def generate_with_grok(home_en, away_en):
    home = translate_team_name(home_en)
    away = translate_team_name(away_en)
    
    prompt = f"""你是一位專業香港足球分析員，用香港足球術語為 {home} vs {away} 寫完整8大板塊預測。"""

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-4.3",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=40)
        if r.status_code == 200:
            print("✅ Grok 成功生成")
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Grok 錯誤:", e)
    
    return f"""⚽️ **【世界盃：{home} vs {away}】**
**8️⃣ 最終總結**：看好{home}勝出，建議**受讓**或**大球**。中場用派彩快調整！"""

# ====================== 發送 ======================
def send_to_channel(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    print("Telegram 回應:", response.json())

# ====================== 主程式 ======================
if __name__ == "__main__":
    matches = get_today_matches()
    for m in matches:
        report = generate_with_grok(m["home"], m["away"])
        send_to_channel(report)
        print(f"✅ 已處理：{m['home']} vs {m['away']}")
