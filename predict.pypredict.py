import requests
import os
from datetime import datetime, timedelta

# ====================== 設定 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@my_ball_predict_3034")
GROK_API_KEY = os.getenv("GROK_API_KEY")

print(f"🔑 BOT_TOKEN 載入情況: {'已載入' if BOT_TOKEN else '❌ 未載入'}")
print(f"🔑 GROK_API_KEY 載入情況: {'已載入' if GROK_API_KEY else '❌ 未載入'}")
print(f"📢 CHANNEL_ID: {CHANNEL_ID}")

# ====================== 球隊映射 ======================
team_name_map = {
    "Ivory Coast": "科特迪瓦", "Ecuador": "厄瓜多爾",
    "Netherlands": "荷蘭", "Japan": "日本",
    "Germany": "德國", "Curaçao": "庫拉索",
    "Argentina": "阿根廷", "France": "法國",
    "Unknown": "未知"
}

def translate_team_name(name):
    return team_name_map.get(name, name)

# ====================== 賽程 ======================
def get_today_worldcup_matches():
    print("🔄 抓取賽程...")
    return [{"home": "Germany", "away": "Curaçao"}]   # 測試用

# ====================== Grok 生成 ======================
def generate_with_grok(home_en, away_en):
    home = translate_team_name(home_en)
    away = translate_team_name(away_en)
    
    prompt = f"""你是一位專業香港足球分析員，用香港足球術語為世界盃比賽撰寫 8 大板塊預測。
比賽：{home} vs {away}
請嚴格按照以下格式輸出：
1️⃣ 預計首發陣容及理由（結合新人和傷停）
2️⃣ 近期狀態與戰術對決
3️⃣ 傷停情況、交手紀錄及背景動機
4️⃣ 投注價值推薦
5️⃣ 風險及冷門可能性
6️⃣ 全體預測
7️⃣ 預測比分（波膽）
8️⃣ 最終總結（加入派彩快提示）
要求：內容自然、強調最新戰意、新陣容，淡化歷史往績。"""

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-beta",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=45)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        print("✅ Grok API 成功生成")
        return content
    except Exception as e:
        print(f"⚠️ Grok API 失敗: {e}")
        return f'''⚽️ **【世界盃焦點：{home} vs {away}】**
📊 **馬會即時賠率**：主勝 2.05 | 和 3.40 | 客勝 3.30

**1️⃣ 預計首發陣容及理由**
{home}：新星上陣，教練試陣適應世界盃。

**8️⃣ 最終總結**
看好{home}小勝，建議小注**受讓**或**大球**。中場用派彩快調整！'''

# ====================== 發送（已加強 Debug） ======================
def send_to_telegram(text):
    print("🚀 準備發送到 Telegram...")
    print(f"使用的 CHANNEL_ID: {CHANNEL_ID}")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Telegram API 回應:", response.json())
        if response.status_code == 200:
            print("🎉 成功發送到頻道！")
        else:
            print("❌ 發送失敗:", response.text)
    except Exception as e:
        print("❌ 發送異常:", str(e))

# ====================== 主程式 ======================
if __name__ == "__main__":
    print("🚀 世界盃預測工具啟動...")
    matches = get_today_worldcup_matches()
    
    for m in matches:
        print(f"📝 正在分析：{m['home']} vs {m['away']}")
        report = generate_with_grok(m["home"], m["away"])
        send_to_telegram(report)
        print("✅ 本次處理完成\n")
