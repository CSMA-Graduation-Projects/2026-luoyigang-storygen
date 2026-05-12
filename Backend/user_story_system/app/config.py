from autogen_ext.models.openai import OpenAIChatCompletionClient

def get_model_client():
    return OpenAIChatCompletionClient(
        model="deepseek-v4-flash",
        api_key= "sk-479248053a014a7f89857eff384524b1",
        base_url="https://api.deepseek.com/v1",
        temperature=0.3,
        model_info={
            "family": "openai",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": False
        }
    )