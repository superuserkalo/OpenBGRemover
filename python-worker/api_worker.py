from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from image_processor import BRIABackground # Imports your class from the other file
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# Load the model once on startup. This is efficient.
logging.info("Loading Bria Background model...")
processor = BRIABackground()
logging.info("Model loaded successfully.")

@app.post("/remove")
async def remove_background_api(file: UploadFile = File(...)):
    """
    API endpoint to remove the background from an uploaded image.
    """
    # Read image bytes directly from the uploaded file
    image_bytes = await file.read()

    # Load bytes into a PIL Image object in memory
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logging.error(f"Failed to open image: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e}")

    logging.info(f"Processing image of size {image.size}...")

    # Process the in-memory PIL image using your class method
    processed_image_pil = processor.process_image(image)

    # Save the output image to an in-memory byte buffer
    output_buffer = io.BytesIO()
    processed_image_pil.save(output_buffer, format="PNG")
    output_buffer.seek(0) # Rewind the buffer to the beginning

    logging.info("Processing complete. Sending response.")

    # Return the processed image as a PNG response
    return Response(content=output_buffer.getvalue(), media_type="image/png")
