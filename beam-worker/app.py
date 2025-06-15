# beam_worker.py
"""
Production-ready Beam worker for background removal.
Handles both static images (PNG, JPG, WEBP) and animated GIFs.
"""
from beam import endpoint, Image, env, Volume
import base64
import io
from typing import Dict, Any, Optional, Tuple, List
import time
import gc

# Only import heavy dependencies in remote environment
if env.is_remote():
    import os
    import torch
    from PIL import Image as PILImage, ImageFilter, ImageSequence
    import numpy as np
    from transformers import AutoModelForImageSegmentation
    from scipy import ndimage
    from torchvision import transforms

def load_model():
    """Initialize model once when container starts"""
    print("🚀 Loading BRIA RMBG-2.0 model...")

    # Use cache directory for model persistence
    cache_dir = "./model_cache"
    os.environ["HUGGINGFACE_HUB_CACHE"] = cache_dir

    # Load model
    model = AutoModelForImageSegmentation.from_pretrained(
        'briaai/RMBG-2.0',
        trust_remote_code=True,
        cache_dir=cache_dir
    )

    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.set_float32_matmul_precision('highest')
    model.to(device)
    model.eval()

    # Preprocessing pipeline
    transform = transforms.Compose([
        transforms.Resize((1024, 1024), antialias=True),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    print(f"✅ Model loaded successfully on {device}")
    return model, transform, device


# Quality presets
QUALITY_PRESETS = {
    "auto": {"mask_offset": -1, "mask_blur": 0.5, "edge_sharpness": 30, "threshold": 0.015},
    "quality": {"mask_offset": -2, "mask_blur": 1.0, "edge_sharpness": 40, "threshold": 0.02},
    "portrait": {"mask_blur": 2.0, "edge_sharpness": 10, "threshold": 0.01},
    "product": {"mask_blur": 0, "edge_sharpness": 60, "threshold": 0.05, "mask_offset": -2},
    "speed": {"mask_blur": 0, "edge_sharpness": 0, "threshold": 0.01}
}

# GIF processing limits
MAX_GIF_FRAMES = 500  # Prevent memory issues
MAX_GIF_PIXELS = 10_000_000  # 10 megapixels per frame


@endpoint(
    name="bg-removal",
    cpu=2,  # Increased for GIF processing
    memory="8Gi",  # Increased for large GIFs
    gpu="RTX4090",
    image=Image(python_version="python3.12")
    .add_python_packages([
        "torch==2.7.1",
        "torchvision==0.22.1",
        "transformers==4.52.4",
        "scipy==1.15.3",
        "pillow==11.2.1",
        "numpy==2.3.0",
        "timm==1.0.15",
        "kornia==0.8.1"
    ]),
    volumes=[Volume(name="model_cache", mount_path="./model_cache")],
    on_start=load_model,
    secrets=["HUGGING_FACE_HUB_TOKEN"],
    keep_warm_seconds=300,  # Keep warm for 5 minutes
    max_pending_tasks=100,
    timeout=180,  # Increased timeout for GIFs
)
def remove_background(context, **inputs) -> Dict[str, Any]:
    """
    Remove background from image or animated GIF.

    Expected inputs:
    - image: base64 encoded image data
    - quality: preset name (default: 'auto')
    - format: output format (default: 'png')
    - return_mask: whether to return the mask (default: False)
    - resize: optional resize parameters

    Returns:
    - success: boolean
    - image: base64 encoded result
    - mask: base64 encoded mask (if requested)
    - error: error message (if failed)
    - metadata: processing metadata
    """

    start_time = time.time()

    # --- Helper function for processing a single frame ---
    def _process_single_frame(image: PILImage.Image, settings: dict, original_image_bytes: bytes = None) -> Tuple[PILImage.Image, PILImage.Image]:
        """Process one frame, returns (final_image, mask_pil)"""
        model, transform, device = context.on_start_value
        original_frame_size = image.size

        # Reduce memory usage for very large frames
        scale_factor = 1.0
        if original_frame_size[0] * original_frame_size[1] > 4_000_000:  # 4MP
            scale_factor = (4_000_000 / (original_frame_size[0] * original_frame_size[1])) ** 0.5
            scaled_size = (int(original_frame_size[0] * scale_factor),
                          int(original_frame_size[1] * scale_factor))
            image = image.resize(scaled_size, PILImage.Resampling.LANCZOS)

        input_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            preds = model(input_tensor)[-1].sigmoid().cpu()

        mask_tensor = preds[0].squeeze()
        mask_np = mask_tensor.numpy()

        # Apply post-processing
        threshold = settings.get('threshold', 0.01)
        if threshold > 0:
            mask_np[mask_np < threshold] = 0

        edge_sharpness = settings.get('edge_sharpness', 0)
        if edge_sharpness > 0:
            k = edge_sharpness / 2
            mask_np = 1 / (1 + np.exp(-k * (mask_np - 0.5)))

        # Convert mask to PIL
        mask_pil = transforms.ToPILImage()(torch.from_numpy(mask_np))
        mask_pil = mask_pil.resize(original_frame_size, PILImage.Resampling.LANCZOS)

        # Apply morphological operations
        mask_offset = settings.get('mask_offset', 0)
        if mask_offset != 0:
            binary_mask = np.array(mask_pil) > 127
            if mask_offset > 0:
                processed_mask = ndimage.binary_dilation(binary_mask, iterations=abs(mask_offset))
            else:
                processed_mask = ndimage.binary_erosion(binary_mask, iterations=abs(mask_offset))
            mask_pil = PILImage.fromarray((processed_mask * 255).astype(np.uint8), mode='L')

            # Re-soften edges after morphological operations
            re_soften_blur = abs(mask_offset) / 4.0 + 1.0
            mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=re_soften_blur))

        # Apply final blur
        mask_blur = settings.get('mask_blur', 0)
        if mask_blur > 0:
            mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=mask_blur))

        # Create final image with alpha channel
        if scale_factor == 1.0:
            final_frame = image.copy()
        else:
            # If we downscaled, reload original for final output
            if original_image_bytes:
                final_frame = PILImage.open(io.BytesIO(original_image_bytes)).convert("RGB")
            else:
                final_frame = image.resize(original_frame_size, PILImage.Resampling.LANCZOS)

        final_frame.putalpha(mask_pil)

        # Clear memory
        del input_tensor
        if device.type == 'cuda':
            torch.cuda.empty_cache()

        return final_frame, mask_pil

    # --- Process frames in batches for better GPU utilization ---
    def _process_gif_frames_batch(frames: List[PILImage.Image], settings: dict, batch_size: int = 4) -> List[PILImage.Image]:
        """Process GIF frames in batches for better performance"""
        processed_frames = []

        for i in range(0, len(frames), batch_size):
            batch = frames[i:i + batch_size]
            batch_results = []

            for frame in batch:
                result, _ = _process_single_frame(frame.convert("RGB"), settings)
                batch_results.append(result)

            processed_frames.extend(batch_results)

            # Log progress for long GIFs
            if len(frames) > 50:
                progress = (i + len(batch)) / len(frames) * 100
                print(f"📊 Progress: {progress:.1f}% ({i + len(batch)}/{len(frames)} frames)")

        return processed_frames

    try:
        # Validate inputs
        if 'image' not in inputs:
            return {
                "success": False,
                "error": "No image provided",
                "code": "MISSING_IMAGE"
            }

        # Get model from context
        model, transform, device = context.on_start_value

        # Decode image
        try:
            image_bytes = base64.b64decode(inputs['image'])
            image = PILImage.open(io.BytesIO(image_bytes))
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid image data: {str(e)}",
                "code": "INVALID_IMAGE"
            }

        # Check if animated
        is_animated = getattr(image, 'is_animated', False)
        n_frames = getattr(image, 'n_frames', 1) if is_animated else 1
        original_size = image.size

        # Validate image/GIF size
        if is_animated:
            if n_frames > MAX_GIF_FRAMES:
                return {
                    "success": False,
                    "error": f"GIF has too many frames ({n_frames}). Maximum is {MAX_GIF_FRAMES}.",
                    "code": "TOO_MANY_FRAMES"
                }
            if original_size[0] * original_size[1] > MAX_GIF_PIXELS:
                return {
                    "success": False,
                    "error": f"GIF frames are too large. Maximum is {MAX_GIF_PIXELS} pixels per frame.",
                    "code": "GIF_TOO_LARGE"
                }
        else:
            if original_size[0] * original_size[1] > 25_000_000:
                return {
                    "success": False,
                    "error": "Image too large. Maximum 25 megapixels.",
                    "code": "IMAGE_TOO_LARGE"
                }

        # Get processing parameters
        quality = inputs.get('quality', 'auto')
        if quality not in QUALITY_PRESETS:
            quality = 'auto'

        settings = QUALITY_PRESETS[quality].copy()

        # Allow custom parameter overrides
        for param in ['threshold', 'edge_sharpness', 'mask_blur', 'mask_offset']:
            if param in inputs:
                settings[param] = inputs[param]

        # Process image(s)
        final_image = None
        mask_pil = None

        if is_animated:
            print(f"🎞️ Processing animated GIF with {n_frames} frames...")

            # Extract all frames first
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(image):
                frames.append(frame.copy())
                durations.append(frame.info.get('duration', 100))

            # Process frames in batches
            processed_frames = _process_gif_frames_batch(frames, settings)

            # Create output GIF
            if processed_frames:
                gif_buffer = io.BytesIO()
                processed_frames[0].save(
                    gif_buffer,
                    format='GIF',
                    save_all=True,
                    append_images=processed_frames[1:],
                    duration=durations,
                    loop=image.info.get('loop', 0),
                    transparency=0,
                    disposal=2,
                    optimize=True  # Optimize GIF size
                )
                gif_buffer.seek(0)
                final_image = PILImage.open(gif_buffer)

            # Clear memory
            del frames, processed_frames
            gc.collect()

        else:
            print("🖼️ Processing static image...")
            image_rgb = image.convert("RGB")
            final_image, mask_pil = _process_single_frame(image_rgb, settings, image_bytes)

        # Handle resizing if requested
        output_size = final_image.size if final_image else original_size
        if 'resize' in inputs and isinstance(inputs['resize'], dict) and final_image:
            resize_config = inputs['resize']
            target_width = resize_config.get('width')
            target_height = resize_config.get('height')
            keep_aspect = resize_config.get('keep_aspect', True)

            if target_width and target_height:
                if keep_aspect:
                    # Calculate aspect-preserving dimensions
                    aspect = original_size[0] / original_size[1]
                    if target_width / target_height > aspect:
                        target_width = int(target_height * aspect)
                    else:
                        target_height = int(target_width / aspect)

                if is_animated:
                    # Resize animated GIF frames
                    resized_frames = []
                    for frame in ImageSequence.Iterator(final_image):
                        resized_frame = frame.resize((target_width, target_height), PILImage.Resampling.LANCZOS)
                        resized_frames.append(resized_frame)

                    gif_buffer = io.BytesIO()
                    resized_frames[0].save(
                        gif_buffer,
                        format='GIF',
                        save_all=True,
                        append_images=resized_frames[1:],
                        duration=durations if 'durations' in locals() else 100,
                        loop=image.info.get('loop', 0),
                        transparency=0,
                        disposal=2,
                        optimize=True
                    )
                    gif_buffer.seek(0)
                    final_image = PILImage.open(gif_buffer)
                else:
                    final_image = final_image.resize(
                        (target_width, target_height),
                        PILImage.Resampling.LANCZOS
                    )
                    if mask_pil and inputs.get('return_mask', False):
                        mask_pil = mask_pil.resize(
                            (target_width, target_height),
                            PILImage.Resampling.LANCZOS
                        )

                output_size = (target_width, target_height)

        # Encode output
        output_format = 'gif' if is_animated else inputs.get('format', 'png').lower()
        img_buffer = io.BytesIO()

        if output_format == 'gif':
            final_image.save(img_buffer, format='GIF', save_all=True, optimize=True)
        elif output_format == 'webp':
            final_image.save(img_buffer, format='WEBP', quality=95, method=6)
        else:
            final_image.save(img_buffer, format='PNG', optimize=True)

        img_buffer.seek(0)
        image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        # Prepare response
        processing_time = int((time.time() - start_time) * 1000)

        response = {
            "success": True,
            "image": image_base64,
            "metadata": {
                "original_size": list(original_size),
                "output_size": list(output_size),
                "processing_time_ms": processing_time,
                "quality_used": quality,
                "format": output_format,
                "device": str(device),
                "is_animated": is_animated,
                "frame_count": n_frames,
            }
        }

        # Add mask if requested (only for static images)
        if inputs.get('return_mask', False) and mask_pil and not is_animated:
            mask_buffer = io.BytesIO()
            mask_pil.save(mask_buffer, format='PNG', optimize=True)
            mask_buffer.seek(0)
            response['mask'] = base64.b64encode(mask_buffer.getvalue()).decode('utf-8')

        return response

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error processing image: {error_trace}")

        return {
            "success": False,
            "error": str(e),
            "code": "PROCESSING_ERROR",
            "trace": error_trace if inputs.get('debug', False) else None
        }

'''
# Health check endpoint (lightweight)
@endpoint(
    name="bg-removal-health",
    cpu=0.5,
    memory="512Mi",
)
def health_check(**inputs):
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "bg-removal-worker",
        "version": "2.0.0",  # Version bump for GIF support
        "features": ["static_images", "animated_gifs"],
        "timestamp": time.time()
    }
'''
