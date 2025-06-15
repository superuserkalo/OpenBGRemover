import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
from PIL import Image, ImageFilter, ImageOps
import torch
from torchvision import transforms
from transformers import AutoModelForImageSegmentation
import numpy as np
from typing import Optional, Tuple, Union

class BRIABackground:
    """
    Optimized BRIA RMBG-2.0 implementation with all best practices.
    """

    def __init__(self, device: Optional[str] = None, precision: str = 'highest'):
        """
        Initialize the BRIA background remover.

        Args:
            device: Device to use ('cuda', 'mps', 'cpu', or None for auto-detect)
            precision: Float32 matmul precision ('high' or 'highest')
        """
        # Device selection
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif torch.backends.mps.is_available():
                self.device = torch.device("mps")
                torch.mps.empty_cache()
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        print(f"Using device: {self.device}")

        # Load model
        self.model = AutoModelForImageSegmentation.from_pretrained(
            'briaai/RMBG-2.0',
            trust_remote_code=True
        )

        # Set precision for better performance
        torch.set_float32_matmul_precision(precision)

        self.model.to(self.device)
        self.model.eval()

        # Define transform
        self.transform = transforms.Compose([
            transforms.Resize((1024, 1024)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def process_image(
        self,
        image_path: str,
        output_path: str,
        mask_blur: float = 0,
        mask_offset: int = 0,
        edge_sharpness: float = 0,
        threshold_low: float = 0.0,
        threshold_high: float = 1.0,
        antialias: bool = True,
        return_mask: bool = False
    ) -> Optional[Image.Image]:
        """
        Remove background from an image with advanced options.

        Args:
            image_path: Path to input image
            output_path: Path to save output image
            mask_blur: Blur applied to mask edges (0-10)
            mask_offset: Expand/shrink mask boundary (-50 to 50)
            edge_sharpness: Sharpness of edges (0-100, 0=soft, 100=very sharp)
            threshold_low: Values below this become 0 (0.0-0.5)
            threshold_high: Values above this become 1 (0.5-1.0)
            antialias: Apply antialiasing to edges
            return_mask: If True, also return the mask

        Returns:
            The mask as PIL Image if return_mask=True, else None
        """
        # Load image
        image = Image.open(image_path).convert("RGB")
        original_size = image.size

        # Transform image
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # Get prediction
        with torch.no_grad():
            # Use [-1] to get the final output layer (official method)
            preds = self.model(input_tensor)[-1].sigmoid().cpu()

        # Extract and process mask
        mask = preds[0].squeeze()

        # Convert to numpy for advanced processing
        mask_np = mask.numpy()

        # Apply edge sharpness if specified
        if edge_sharpness > 0:
            # Sigmoid curve for sharpening
            k = edge_sharpness / 2  # Scale to reasonable range
            mask_np = 1 / (1 + np.exp(-k * (mask_np - 0.5)))

        # Apply thresholding if specified
        if threshold_low > 0:
            mask_np = np.where(mask_np < threshold_low, 0, mask_np)
        if threshold_high < 1.0:
            mask_np = np.where(mask_np > threshold_high, 1, mask_np)

        # Convert to PIL and resize to original size
        mask_pil = transforms.ToPILImage()(torch.from_numpy(mask_np))
        mask_pil = mask_pil.resize(original_size, Image.Resampling.LANCZOS)

        # Apply mask offset (expand/shrink)
        if mask_offset != 0:
            mask_np = np.array(mask_pil).astype(np.float32) / 255.0

            if mask_offset > 0:
                # Dilate (expand)
                from scipy import ndimage
                mask_np = ndimage.binary_dilation(mask_np > 0.5, iterations=abs(mask_offset))
            else:
                # Erode (shrink)
                from scipy import ndimage
                mask_np = ndimage.binary_erosion(mask_np > 0.5, iterations=abs(mask_offset))

            mask_pil = Image.fromarray((mask_np * 255).astype(np.uint8), mode='L')

        # Apply blur if specified
        if mask_blur > 0:
            mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=mask_blur))

        # Apply antialiasing
        if antialias:
            # Find edges and apply selective smoothing
            edges = mask_pil.filter(ImageFilter.FIND_EDGES)
            smooth_mask = mask_pil.filter(ImageFilter.SMOOTH_MORE)
            # Composite smooth edges with original mask
            mask_pil = Image.composite(smooth_mask, mask_pil, edges.point(lambda x: 255 if x > 20 else 0))

        # Apply mask to create final image
        image.putalpha(mask_pil)

        # Save result
        image.save(output_path, 'PNG', optimize=True)
        print(f"Success! Background removed. Output saved to {output_path}")

        if return_mask:
            return mask_pil
        return None

    def process_batch(
        self,
        input_folder: str,
        output_folder: str,
        **kwargs
    ):
        """
        Process all images in a folder.

        Args:
            input_folder: Input folder path
            output_folder: Output folder path
            **kwargs: Additional arguments passed to process_image
        """
        import os
        from pathlib import Path

        # Create output folder
        Path(output_folder).mkdir(exist_ok=True)

        # Supported formats
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}

        # Get all image files
        image_files = [f for f in os.listdir(input_folder)
                      if any(f.lower().endswith(ext) for ext in extensions)]

        print(f"Found {len(image_files)} images to process")

        # Process each image
        for i, filename in enumerate(image_files):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + '_nobg.png'
            output_path = os.path.join(output_folder, output_filename)

            try:
                print(f"\n[{i+1}/{len(image_files)}] Processing: {filename}")
                self.process_image(input_path, output_path, **kwargs)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")


def quick_remove_bg(input_path: str, output_path: str, quality: str = "balanced"):
    """
    Quick function for easy background removal with presets.

    Args:
        input_path: Input image path
        output_path: Output image path
        quality: Preset quality mode:
            - "soft": Best for portraits with hair
            - "balanced": General purpose (default)
            - "sharp": Best for objects with clear edges
            - "ultra_sharp": For graphics/logos
    """
    # Initialize processor
    processor = BRIABackground()

    # Define presets
    presets = {
        "soft": {
            "mask_blur": 1.5,
            "edge_sharpness": 10,
            "antialias": True
        },
        "balanced": {
            "mask_blur": 0.5,
            "edge_sharpness": 30,
            "threshold_low": 0.01,
            "antialias": True
        },
        "sharp": {
            "mask_blur": 0,
            "edge_sharpness": 50,
            "threshold_low": 0.05,
            "threshold_high": 0.95,
            "antialias": True
        },
        "ultra_sharp": {
            "mask_blur": 0,
            "edge_sharpness": 80,
            "threshold_low": 0.1,
            "threshold_high": 0.9,
            "antialias": False
        }
    }

    # Get preset settings
    settings = presets.get(quality, presets["balanced"])

    # Process image
    processor.process_image(input_path, output_path, **settings)


# --- Example Usage ---
if __name__ == "__main__":
    # Method 1: Quick removal with presets
    quick_remove_bg('lumi.jpg', 'output_balanced.png', quality='balanced')
    quick_remove_bg('lumi.jpg', 'output_sharp.png', quality='sharp')

    # Method 2: Advanced usage with custom parameters
    processor = BRIABackground(precision='highest')

    # For portraits with fine hair detail
    processor.process_image(
        'lumi.jpg',
        'portrait_nobg.png',
        mask_blur=1.0,
        edge_sharpness=20,
        antialias=True
    )

    # For product photos with clean edges
    processor.process_image(
        'lumi.jpg',
        'product_nobg.png',
        mask_blur=0,
        edge_sharpness=60,
        threshold_low=0.05,
        threshold_high=0.95,
        antialias=True
    )

    # For logos/graphics
    processor.process_image(
        'lumi.jpg',
        'logo_nobg.png',
        edge_sharpness=100,
        threshold_low=0.2,
        threshold_high=0.8,
        antialias=False
    )

    # Batch processing
    '''processor.process_batch(
        'input_folder/',
        'output_folder/',
        edge_sharpness=30,
        antialias=True
    )'''
