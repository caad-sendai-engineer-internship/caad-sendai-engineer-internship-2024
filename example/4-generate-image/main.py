import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI
from openai.types import ImagesResponse

load_dotenv()


def generate_image(prompt: str) -> ImagesResponse:
    client = AzureOpenAI(
        api_version=os.environ["OPENAI_API_VERSION"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )

    result = client.images.generate(
        model=os.environ["AZURE_OPENAI_IMAGE_MODEL_DEPLOYMENT_NAME"],
        prompt=prompt,
        n=1,
    )

    return result


# Create prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "You are an image generation assistant. For every request, create a specific and detailed prompt in English to generate an image using 'DALL-E 3'. The prompt should clearly describe all elements of the requested image, including background, characters, objects, colors, and style. Additionally, ensure that the prompts adhere to DALL-E 3's policy guidelines. For any content that might violate these policies, use indirect expressions to avoid direct violations while still achieving the desired outcome."
        ),
        ("user", "{image_desc}"),
    ]
)

# Create llm
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME"],
    temperature=0,
)

# Create parser
parser = StrOutputParser()

# Create chain
chain = prompt | llm | parser | RunnableLambda(generate_image)
# response = chain.invoke({"image_desc": "メガネのおじさん"})
# print(response)


# App definition
app = FastAPI()


# Adding route
@app.get("/generate-image", tags=["Generate Image"])
async def generate_image_route(image_desc: str):
    response = chain.invoke({"image_desc": image_desc})
    return RedirectResponse(url=response.data[0].url)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
