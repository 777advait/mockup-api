from io import BytesIO
import os
import logging
import concurrent.futures
from PIL import Image
import requests
from generate_mockup import generate_mockup
from create_maps import create_maps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='mockup_processing.log'
)

# Existing path configurations
PATH_CONFIG = {
    'template_image': 'base_images/template.jpg',
    'mask_image': 'base_images/mask.png',
    'displacement_map': 'maps/displacement_map.png',
    'lighting_map': 'maps/lighting_map.png',
    'adjustment_map': 'maps/adjustment_map.jpg'
}


def resize_swatch_with_error_handling(path_to_base_image, image_content, output_file, bottom_padding=300):
    try:
        with Image.open(path_to_base_image) as base_image, Image.open(BytesIO(image_content)) as swatch_image:
            base_width, base_height = base_image.size
            swatch_width, swatch_height = swatch_image.size

            new_width = 400
            new_height = int((new_width / swatch_width) * swatch_height)
            swatch_image = swatch_image.resize(
                (new_width, new_height), Image.LANCZOS)

            new_image = Image.new(
                "RGB", (base_width, base_height), (255, 255, 255))

            paste_x = (base_width - new_width) // 2
            paste_y = base_height - new_height - bottom_padding
            paste_y = max(0, paste_y)

            new_image.paste(swatch_image, (paste_x, paste_y))
            new_image.save(output_file, optimize=True, quality=85)

        logging.info(f"Resized and saved swatch image to: {output_file}")
        print(f"Resized and saved swatch image to: {output_file}")
        return output_file

    except Exception as e:
        logging.error(f"Error resizing image: {e}")
        print(f"Error resizing image: {e}")
        return None


def process_single_mockup(image_content, output_file):
    """
    Process a single mockup image by resizing the swatch and applying mockup generation.

    Args:
        image_content (bytes): byte stream of the swatch image to be processed.
        output_file (str): Filename of the output mockup image.

    Returns:
        str: Result message indicating success or error.
    """
    try:
        resized_image = resize_swatch_with_error_handling(
            PATH_CONFIG['template_image'], image_content, output_file)
        if resized_image is None:
            raise Exception('Error resizing image')

        generate_mockup(
            PATH_CONFIG['template_image'],
            PATH_CONFIG['mask_image'],
            resized_image,
            PATH_CONFIG['displacement_map'],
            PATH_CONFIG['lighting_map'],
            PATH_CONFIG['adjustment_map'],
            output_file
        )

        logging.info(f"Successfully processed mockup: {output_file}")
        return f"Success: {output_file}"

    except Exception as e:
        logging.error(f"Comprehensive error processing mockup: {e}")
        raise RuntimeError(f"Error: {str(e)}")


def create_mockups(image_urls):
    """
    Main function to generate mockups for a list of swatch images concurrently.

    Args:
        images_list (List[str]): List of images to generate mockup of.

    Returns:
        List[str]: Results for each image processed.
    """
    # Ensure directories exist
    os.makedirs('mockups', exist_ok=True)

    # Create maps once (only needs to be done at the beginning)
    create_maps(PATH_CONFIG['template_image'], PATH_CONFIG['mask_image'])
    logging.info("Base maps created successfully")

    # Use ThreadPoolExecutor for concurrent processing of images
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {}
        for image_url in image_urls:
            try:
                response = requests.get(image_url)

                if (response.status_code != 200 or not response.content or not response.headers.get('content-type').startswith('image/')):
                    logging.error(f"Failed to download image from {image_url}")
                    raise RuntimeError(
                        f"Error: Failed to download image from {image_url}")

                filename = os.path.basename(image_url)

                output_file = os.path.join('mockups', filename)
                futures[executor.submit(
                    process_single_mockup, response.content, output_file)] = image_url

            except Exception as e:
                logging.error(f"Error processing {image_url}: {e}")
                print(f"Error processing {image_url}: {e}")
                raise RuntimeError(f"Error processing {image_url}")

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(results)

    logging.info("Mockup generation completed for all images")
    return results
