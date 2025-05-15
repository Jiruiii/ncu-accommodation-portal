import os
import requests # type: ignore

def send_sms(phone_number, message):
    """
    發送簡訊 (使用 TwilioAPI 或其他簡訊服務)
    
    參數:
        phone_number (str): 接收簡訊的手機號碼
        message (str): 簡訊內容
    """
    # 這裡使用 Twilio API 作為示例
    # 實際開發中，請替換為您選擇的簡訊服務商
    
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # 判斷是否為測試環境
    is_test = os.environ.get('FLASK_ENV') == 'development'
    
    if is_test:
        # 測試環境，模擬發送
        print(f"[TEST MODE] 簡訊將發送到 {phone_number}: {message}")
        return True
    
    if not all([account_sid, auth_token, from_number]):
        raise Exception("缺少簡訊發送所需的環境變數")
    
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        payload = {
            'To': phone_number,
            'From': from_number,
            'Body': message
        }
        
        response = requests.post(
            url, 
            data=payload, 
            auth=(account_sid, auth_token)
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"簡訊發送失敗: {response.text}")
            
        print(f"成功發送簡訊到 {phone_number}")
        return True
    except Exception as e:
        print(f"發送簡訊失敗: {str(e)}")
        raise e