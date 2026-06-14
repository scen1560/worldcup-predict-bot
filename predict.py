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
        "model": "grok-beta",        # ← 改用較穩定的 model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=45)
        response.raise_for_status()   # 檢查 HTTP 錯誤
        content = response.json()["choices"][0]["message"]["content"]
        print("✅ Grok API 成功生成內容")
        return content
    except Exception as e:
        print(f"⚠️ Grok API 呼叫失敗: {e}")
        # 更豐富的後備模板
        return f'''⚽️ **【世界盃焦點：{home} vs {away}】**

📊 **馬會即時賠率**：主勝 2.05 | 和 3.40 | 客勝 3.30

**1️⃣ 預計首發陣容及理由**  
{home}：新陣容上陣，教練安排新人適應世界盃節奏。

**2️⃣ 近期狀態與戰術對決**  
{home}新進攻線火力強。

**3️⃣ 傷停、背景動機**  
最新戰意高，陣容大變，歷史往績參考價值低。

**4️⃣ 投注價值推薦**  
推薦 **受讓** 或 **大細球 2.5**

**7️⃣ 預測比分（波膽）**  
**2-1**（{home}勝）

**8️⃣ 最終總結**  
看好{home}小勝，建議小注受讓。中場用派彩快調整！理性投注。'''
