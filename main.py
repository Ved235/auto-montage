from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=""
)

image_path = "test.png"

result = CLIENT.infer(image_path, model_id="valorant-kills/1")

print(result)