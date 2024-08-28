import json
import os
import unicodedata

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from constants import WORKING_DIRECTORY
from workflows.super import create_super_workflow

load_dotenv()


class ConversationResponse(BaseModel):
    message: str
    attachment_files: list[str]


class ErrorResponse(BaseModel):
    detail: str


app = FastAPI()

chain = create_super_workflow()
# response = chain.invoke(
#     {"messages": [("human", "日本の人口の男女比の割合の円グラフを作成してください。")]},
#     {"messages": [("human", "なんでもいいので円グラフを作成してください。")]},
#     {"messages": [("human", "コーラ70%、ペプシ30%の円グラフを作成してください。")]},
#     {"messages": [("human", "こんにちは！")]},
#     config={"configurable": {"thread_id": "1"}},
# )
# print(response)


@app.get(
    f"/conversation/{WORKING_DIRECTORY}/{{thread_id}}/{{file_name}}",
    response_class=FileResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["conversation"],
)
async def download_file(thread_id: str, file_name: str):
    file_path = f"{WORKING_DIRECTORY}/{thread_id}/{file_name}"
    if os.path.isfile(file_path):
        return file_path

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


@app.post(
    "/conversation",
    response_model=ConversationResponse,
    tags=["conversation"],
)
async def conversation(
    request: Request,
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

    response = json.loads(response)

    return ConversationResponse(
        message=response["final_answer"],
        attachment_files=[
            f"{request.url}/{thread_working_directory}/{attachment_file}"
            for attachment_file in response.get("attachment_files", [])
        ],
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
