import requests
import json
import time
import hashlib
import hmac
from config import API_KEY, SECRET_KEY, API_URL

MODEL_CONFIGS = {
    "pre_consult": {
        "model": "agent-pre-consultation-v1",
        "name": "预问诊",
        "description": "智能预问诊服务"
    },
    "triage": {
        "model": "agent-triage-v1",
        "name": "分导诊",
        "description": "智能分诊导诊"
    },
    "symptom_diagnosis": {
        "model": "agent-symptom-diagnosis-v1",
        "name": "症状自诊",
        "description": "症状自我诊断"
    },
    "health_qa": {
        "model": "agent-health-qa-v1",
        "name": "健康科普",
        "description": "健康知识问答"
    },
    "drug_consult": {
        "model": "agent-drug-consultation-v1",
        "name": "药品咨询",
        "description": "药品信息咨询"
    },
    "kb_qa": {
        "model": "agent-kb-qa-v1",
        "name": "知识库问答",
        "description": "医疗知识库问答"
    },
    "skin_disease": {
        "model": "agent-skin-disease-v1",
        "name": "皮肤病咨询",
        "description": "皮肤病专业咨询"
    },
    "report_interpret": {
        "model": "agent-report-interpretation-v1",
        "name": "报告解读",
        "description": "体检报告智能解读"
    },
    "medical_vision": {
        "model": "agent-medical-vision-v1",
        "name": "医学视觉溯源",
        "description": "医学影像分析"
    },
    "tcm_diagnose": {
        "model": "agent-tcm-diagnose-v1",
        "name": "中医舌面诊",
        "description": "中医舌诊面诊"
    },
    "clinical_decision": {
        "model": "agent-clinical-decision-v1",
        "name": "临床辅助决策",
        "description": "临床诊疗辅助决策"
    },
    "emr_generation": {
        "model": "agent-emr-generation-v1",
        "name": "对话文本生成病历",
        "description": "对话转病历"
    },
    "health_analysis": {
        "model": "agent-health-qa-v1",
        "name": "健康数据分析",
        "description": "健康数据综合分析"
    },
    "clinical_diagnose": {
        "model": "agent-clinical-diagnose-v1",
        "name": "临床诊断",
        "description": "临床疾病诊断"
    }
}

class LingyiAPI:
    def __init__(self):
        pass

    def generate_signature(self, method, path, body):
        body_md5 = hashlib.md5(body.encode('utf-8')).hexdigest()
        timestamp = time.strftime("%d %b %Y %H:%M:%S GMT", time.localtime())
        auth_string_prefix = f"ihcloud/{API_KEY}/{timestamp}/300"
        canonical_request = f"{method}\n{path}\ncontent-md5:{body_md5}"
        
        signing_key = hmac.new(
            SECRET_KEY.encode('utf-8'),
            auth_string_prefix.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        signature = hmac.new(
            signing_key.encode('utf-8'),
            canonical_request.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        authorization_header = f"{auth_string_prefix}/{signature}"
        return authorization_header

    def chat(self, messages, model="agent-health-qa-v1", stream=False):
        method = "POST"
        path = "/api/ly_llm/v1/chat/completions"

        body = json.dumps({
            "model": model,
            "stream": stream,
            "messages": messages
        }, ensure_ascii=False)

        headers = {
            "Content-Type": "application/json",
            "X-IHU-Authorization-V2": self.generate_signature(method, path, body)
        }

        if stream:
            response = requests.post(API_URL, headers=headers, data=body, stream=True)
            return response
        else:
            response = requests.post(API_URL, headers=headers, data=body)
            return response.json()

    def chat_stream(self, messages, model="agent-health-qa-v1"):
        response = self.chat(messages, model, stream=True)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                try:
                    if line_str.startswith('data:'):
                        data_str = line_str[5:].strip()
                        if data_str and data_str != '[DONE]':
                            data = json.loads(data_str)
                            yield data
                    elif line_str.startswith('event:'):
                        continue
                    else:
                        try:
                            data = json.loads(line_str)
                            yield data
                        except:
                            pass
                except Exception as e:
                    print(f"解析流式响应行失败: {e}, 行内容: {line_str}")
                    continue

    def generic_chat(self, mode, text_input="", image_base64=None, stream=False):
        config = MODEL_CONFIGS.get(mode, MODEL_CONFIGS["health_qa"])
        model = config["model"]
        
        content_list = []
        
        if text_input:
            content_list.append({
                "type": "text",
                "body": text_input
            })
        
        if image_base64:
            content_list.append({
                "type": "image",
                "image": image_base64
            })
        
        if not content_list:
            content_list.append({
                "type": "text",
                "body": "你好"
            })

        messages = [
            {
                "role": "user",
                "content": content_list
            }
        ]

        if stream:
            return self.chat_stream(messages, model=model)
        else:
            return self.chat(messages, model=model)

    def get_model_configs(self):
        return MODEL_CONFIGS
