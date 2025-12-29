from langchain_google_vertexai import ChatVertexAI

def get_llm(temperature: float, max_tokens: int):
    return ChatVertexAI(
        model_name="gemini-2.5-flash",
        temperature=temperature,
        max_output_tokens=max_tokens,
        project="amulate-hackathon",
        location="asia-south1",
    )
