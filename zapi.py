import requests

def send_message(zapi_url, phone, message):
    # zapi_url: URL da instância Z-API. Exemplo: https://api.z-api.io/instances/SEU_INSTANCE/token/SEU_TOKEN
    requests.post(f"{zapi_url}/send-message", json={"phone": phone, "message": message})

def send_image(zapi_url, phone, image_path, caption=""):
    # zapi_url: URL da instância Z-API. Exemplo: https://api.z-api.io/instances/SEU_INSTANCE/token/SEU_TOKEN
    with open(image_path, "rb") as img:
        requests.post(f"{zapi_url}/send-file", files={"file": img}, data={"phone": phone, "caption": caption})

def send_group_message(zapi_url, group_id, message):
    # zapi_url: URL da instância Z-API. Exemplo: https://api.z-api.io/instances/SEU_INSTANCE/token/SEU_TOKEN
    # group_id: ID do grupo de aviso. Exemplo: 5511999999999-grupo
    requests.post(f"{zapi_url}/send-group-message", json={"groupId": group_id, "message": message}) 