# TODO:
# - Add error handling
# - Upload image directly to azure blob without storing locally

from io import BytesIO
import subprocess
import os
import uuid
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings
from datetime import datetime

load_dotenv()


def generate_unique_filename(extension='png'):
    unique_id = uuid.uuid4()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"mockup_{timestamp}_{unique_id}.{extension}"


def generate_mockup(template, mask, artwork, displacement_map, lighting_map, adjustment_map):
    blob_service_client = BlobServiceClient.from_connection_string(
        os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    blob_client = blob_service_client.get_blob_client(
        container=os.getenv("AZURE_STORAGE_CONTAINER_NAME"), blob=generate_unique_filename())

    tmp = 'mpcs/mockup.mpc'

    # Function to run a command and handle errors
    def run_command(cmd):
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True)

    # Get dimensions of the template
    def get_image_size(image_path):
        cmd = ['magick', 'identify', '-format', '%wx%h', image_path]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split('x'))
        return width, height

    # Calculate perspective coordinates based on center alignment
    template_width, template_height = get_image_size(template)

    artwork_width, artwork_height = get_image_size(artwork)

    # Horizontal center
    x_center = template_width // 2

    # Dynamically calculate vertical center based on percentage of template height
    # Adjust as needed (e.g., 0.4 = 40% from top)
    vertical_position_percentage = 0.75
    y_center = int(template_height * vertical_position_percentage) - \
        (artwork_height // 2)

    # Calculate perspective transformation coordinates
    coords = f'0,0,{x_center - artwork_width // 2},{y_center - artwork_height // 2},' \
        f'0,{artwork_height},{x_center - artwork_width // 2},{y_center + artwork_height // 2},' \
        f'{artwork_width},0,{x_center + artwork_width // 2},{y_center - artwork_height // 2},' \
        f'{artwork_width},{artwork_height},{x_center +
                                            artwork_width // 2},{y_center + artwork_height // 2}'

    # Add border
    cmd1 = ['magick', artwork, '-bordercolor',
            'transparent', '-border', '1', tmp]
    run_command(cmd1)

    # Add perspective transform
    cmd2 = [
        'magick', template, '-alpha', 'transparent', '(', tmp, '-distort', 'perspective', coords, ')',
        '-background', 'transparent', '-layers', 'merge', '+repage', tmp
    ]
    run_command(cmd2)

    # Set background color
    cmd3 = ['magick', tmp, '-background',
            'transparent', '-alpha', 'remove', tmp]
    run_command(cmd3)

    # Add displacement
    cmd4 = ['magick', tmp, displacement_map, '-compose', 'displace',
            '-set', 'option:compose:args', '20x20', '-composite', tmp]
    run_command(cmd4)

    # Add highlights
    cmd5 = ['magick', tmp, '(', '-clone', '0', lighting_map, '-compose', 'hardlight',
            '-composite', ')', '+swap', '-compose', 'CopyOpacity', '-composite', tmp]
    run_command(cmd5)

    # Adjust colors
    cmd6 = ['magick', tmp, '(', '-clone', '0', adjustment_map, '-compose', 'multiply',
            '-composite', ')', '+swap', '-compose', 'CopyOpacity', '-composite', tmp]
    run_command(cmd6)

    # Compose artwork
    cmd7 = ['magick', template, tmp, mask, '-compose',
            'over', '-composite', '-resize', '800', 'png:-']
    result = subprocess.run(cmd7, capture_output=True, check=True)

    try:
        blob_client.upload_blob(BytesIO(result.stdout), overwrite=True,
                                content_settings=ContentSettings(content_type="image/png"))
        blob_url = blob_client.url
        print(f"Mockup uploaded successfully to blob")
        return {"url": blob_url}
    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: {e}")

# Example usage:
# generate_mockup('path_to_template_image', 'path_to_mask_image', 'path_to_artwork_image', 'path_to_displacement_map', 'path_to_lighting_map', 'path_to_adjustment_map', 'path_to_output_image')
