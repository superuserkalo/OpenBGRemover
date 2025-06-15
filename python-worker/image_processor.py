# image_processor.py

import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

import torch
from PIL import Image, ImageFilter
import numpy as np
from typing import Optional
from transformers import AutoModelForImageSegmentation
from scipy import ndimage
from pathlib import Path
from torchvision import transforms

class BRIABackground:
    """
    Final optimized implementation.
    Starts with the proven working pipeline and applies
    softness-aware post-processing to fix jagged edges.
    """

    def __init__(self, device: Optional[str] = None, precision: str = 'highest'):
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)
        print(f"Using device: {self.device}")

        self.model = AutoModelForImageSegmentation.from_pretrained(
            'briaai/RMBG-2.0', trust_remote_code=True
        )

        torch.set_float32_matmul_precision(precision)
        self.model.to(self.device)
        self.model.eval()

        # Using the proven pre-processing pipeline
        self.transform = transforms.Compose([
            transforms.Resize((1024, 1024), antialias=True),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def process_image(
        self,
        image: Image.Image, # Now accepts a PIL Image object
        mask_blur: float = 0,
        mask_offset: int = 0,
        edge_sharpness: float = 0,
        threshold: float = 0.01
    ) -> Image.Image:

        original_size = image.size

        # --- Proven pipeline for getting a working mask ---
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            preds = self.model(input_tensor)[-1].sigmoid().cpu()

        mask_tensor = preds[0].squeeze()
        mask_np = mask_tensor.numpy()

        # --- Softness-Aware Post-Processing Pipeline ---
        if threshold > 0:
            mask_np[mask_np < threshold] = 0
        if edge_sharpness > 0:
            k = edge_sharpness / 2
            mask_np = 1 / (1 + np.exp(-k * (mask_np - 0.5)))

        mask_pil = transforms.ToPILImage()(torch.from_numpy(mask_np))
        mask_pil = mask_pil.resize(original_size, Image.Resampling.LANCZOS)

        if mask_offset != 0:
            binary_mask = np.array(mask_pil) > 127
            if mask_offset > 0:
                processed_mask = ndimage.binary_dilation(binary_mask, iterations=abs(mask_offset))
            else:
                processed_mask = ndimage.binary_erosion(binary_mask, iterations=abs(mask_offset))
            mask_pil = Image.fromarray((processed_mask * 255).astype(np.uint8), mode='L')

            re_soften_blur = abs(mask_offset) / 4.0 + 1.0
            mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=re_soften_blur))

        if mask_blur > 0:
            mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=mask_blur))

        # --- Apply the final, smooth mask ---
        final_image = image.copy() # Use a copy to avoid modifying the original
        final_image.putalpha(mask_pil)

        return final_image


def quick_remove_bg(input_path: str, output_path: str, quality: str = "best_quality"):
    """
    High-level convenience function to remove a background from an image file.
    """
    # Initialize the processor once
    processor = BRIABackground()

    # Presets can be tuned here for better quality
    presets = {
        "best_quality": {"mask_offset": -2, "mask_blur": 1.0, "edge_sharpness": 40, "threshold": 0.02},
        "soft_portrait": {"mask_blur": 2.0, "edge_sharpness": 10, "threshold": 0.01},
        "balanced": {"mask_blur": 0.5, "edge_sharpness": 30, "threshold": 0.02},
        "sharp_product": {"mask_blur": 0, "edge_sharpness": 60, "threshold": 0.05, "mask_offset": -2}
    }
    settings = presets.get(quality, presets["best_quality"])

    # Open the image and process it
    image = Image.open(input_path).convert("RGB")
    processed_image = processor.process_image(image, **settings)

    # Save the result
    processed_image.save(output_path, 'PNG')
    print(f"✅ Success! Output saved to {output_path}")
