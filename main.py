from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from wand.image import Image
import io

app = FastAPI()

@app.post("/trim")
async def trim_image(file: UploadFile = File(...)):
    contents = await file.read()
    with Image(blob=contents) as img:
        img.trim()
        buf = io.BytesIO()
        img.save(file=buf, format=img.format)
        buf.seek(0)
    return StreamingResponse(buf, media_type=file.content_type)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
