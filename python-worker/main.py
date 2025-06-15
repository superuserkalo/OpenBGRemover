# main.py
from image_processor import BRIABackground, quick_remove_bg
from PIL import Image

# This is the main script you will run to test your library.
if __name__ == "__main__":

    # --- Method 1: Use the simple, high-level function ---
    print("\n--- Using quick_remove_bg with presets ---")
    # You can easily test different presets here by changing the 'quality'
    # The presets themselves can be tuned in image_processor.py
    quick_remove_bg('lumi.jpg', 'output_quick_best.png', quality='best_quality')
    quick_remove_bg('lumi.jpg', 'output_quick_soft.png', quality='soft_portrait')


    # --- Method 2: Use the class for advanced, direct control ---
    print("\n--- Using the BRIABackground class for advanced control ---")

    # Initialize the processor once for multiple runs (more efficient)
    processor = BRIABackground(precision='highest')

    # Open the image you want to process
    image_to_process = Image.open('lumi.jpg').convert("RGB")

    # Example: A custom setting for a tight, but smooth mask
    processed_image = processor.process_image(
        image=image_to_process,
        mask_offset=-10,
        mask_blur=1.5
    )
    processed_image.save('output_advanced_custom.png')
    print("✅ Success! Advanced custom output saved to output_advanced_custom.png")
