import os
import unicodedata

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel

from constants import WORKING_DIRECTORY
from workflows.workflow import create_workflow

load_dotenv()


class ConversationResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


app = FastAPI()

chain = create_workflow()
# response = chain.invoke(
#     {"messages": [("human", "私がアップロードしたファイルの名前はなんですか？")]},
# )
# print(response)


@app.post(
    "/conversation",
    response_model=ConversationResponse,
    tags=["conversation"],
)
async def conversation(
    thread_id: str = Form(...),
    message: str = Form(...),
    files: list[UploadFile] = File(None),
):
    thread_working_directory = f"{WORKING_DIRECTORY}/{thread_id}"
    if not os.path.isdir(thread_working_directory):
        os.makedirs(thread_working_directory)

    if files:
        for file in files:
            if file.filename:
                file_path = os.path.join(
                    thread_working_directory,
                    unicodedata.normalize("NFC", file.filename),
                )

                if os.path.isfile(file_path):
                    file_name, file_extension = os.path.splitext(file_path)
                    i = 1
                    while os.path.isfile(f"{file_name}_{i}{file_extension}"):
                        i += 1
                    file_path = f"{file_name}_{i}{file_extension}"

                with open(file_path, "wb") as f:
                    f.write(await file.read())

    response = await chain.ainvoke(
        {"messages": [("human", message)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    return ConversationResponse(
        message=response,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # http://127.0.0.1:8000/docs にアクセスして、APIを試してみましょう！
