from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from wand.image import Image
import io
import zipfile

app = FastAPI()


def pdf_to_trimmed_pngs(pdf_bytes: bytes) -> dict:
    output_images = {}

    with Image(blob=pdf_bytes, resolution=150) as pdf:
        for i, page in enumerate(pdf.sequence):
            with Image(page) as img:
                img.format = 'png'
                img.trim()
                buf = io.BytesIO()
                img.save(file=buf)
                buf.seek(0)
                output_images[f"page_{i+1}.png"] = buf.read()

    return output_images


@app.post("/trim-pdf")
async def trim_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    images = pdf_to_trimmed_pngs(contents)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for filename, image_bytes in images.items():
            zf.writestr(filename, image_bytes)
    zip_buffer.seek(0)

    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
        "Content-Disposition": "attachment; filename=trimmed_pages.zip"
    })
