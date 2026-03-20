import requests
import json
import time
import hashlib
import hmac
from config import API_KEY, SECRET_KEY, API_URL

def generate_signature(method, path, body):
    # 1. 计算请求体的 MD5
    body_md5 = hashlib.md5(body.encode('utf-8')).hexdigest()

    # 2. 生成前缀字符串
    timestamp = time.strftime("%d %b %Y %H:%M:%S GMT", time.localtime())
    auth_string_prefix = f"ihcloud/{API_KEY}/{timestamp}/300"

    # 3. 构造规范请求
    canonical_request = f"{method}\n{path}\ncontent-md5:{body_md5}"

    # 4. 生成signingKey: 先用SK对authStringPrefix进行HMAC-SHA256-HEX
    signing_key = hmac.new(
        SECRET_KEY.encode('utf-8'),
        auth_string_prefix.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 5. 生成签名: 用signingKey对canonicalRequest进行HMAC-SHA256-HEX
    signature = hmac.new(
        signing_key.encode('utf-8'),
        canonical_request.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 6. 构造认证头
    authorization_header = f"{auth_string_prefix}/{signature}"
    
    print(f"Timestamp: {timestamp}")
    print(f"Auth String Prefix: {auth_string_prefix}")
    print(f"Body MD5: {body_md5}")
    print(f"Canonical Request: {repr(canonical_request)}")
    print(f"Signing Key: {signing_key}")
    print(f"Signature: {signature}")
    print(f"Authorization Header: {authorization_header}")
    
    return authorization_header

def test_chat():
    method = "POST"
    path = "/api/ly_llm/v1/chat/completions"

    body = json.dumps({
        "model": "agent-health-qa-v1",
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "body": "你好"
                    }
                ]
            }
        ]
    }, ensure_ascii=False)

    headers = {
        "Content-Type": "application/json",
        "X-IHU-Authorization-V2": generate_signature(method, path, body)
    }

    print(f"\nSending request to {API_URL}")
    print(f"Headers: {headers}")
    print(f"Body: {body}")

    response = requests.post(API_URL, headers=headers, data=body)
    
    print(f"\nResponse Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    return response.json()

if __name__ == "__main__":
    try:
        result = test_chat()
        print(f"\nFinal Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())
