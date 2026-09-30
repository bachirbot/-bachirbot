    try:
        d = request.json
        s = d['entry'][0]['messaging'][0]['sender']['id']
        t = d['entry'][0]['messaging'][0]['message']['text'].strip()
        
        # تحديد الرد الذكي بناءً على ما كتبته
        if "سلام" in t or "مرحباً" in t or "كيف حالك" in t:
            reply_text = "أهلاً بك يا بشير! أنا بصحة ممتازة وجاهز لمساعدتك في أعمالك. كيف يمكنني خدمتك اليوم؟"
        elif "من أنت" in t:
            reply_text = "أنا Bachirbot، مساعدك الشخصي الرقمي."
        else:
            reply_text = f"لقد استلمت رسالتك: '{t}'. أنا أعمل بكامل كفاءتي لتنفيذ أوامرك القادمة!"

        # إرسال الرد الذكي عبر الماسنجر
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        requests.post(url, json={"recipient": {"id": s}, "message": {"text": reply_text}})
    except:
        pass
