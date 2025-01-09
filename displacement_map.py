import subprocess


def convert_images(template, mask):
    normalized_template_map_tmp = 'mpcs/normalized_template_map_tmp.mpc'
    brightness_delta = 30
    generate_displacement_map_tmp = 'mpcs/generate_displacement_map_tmp.mpc'
    displacement_map = 'maps/displacement_map.png'

    # Apply mask
    cmd1 = [
        'magick', template, mask, '-alpha', 'off', '-colorspace', 'gray',
        '-compose', 'CopyOpacity', '-composite', normalized_template_map_tmp
    ]
    subprocess.run(cmd1, check=True)

    # Generate displacement map
    cmd2 = [
        'magick', normalized_template_map_tmp, '-evaluate', 'subtract',
        f'{brightness_delta}%', '-background', 'grey50', '-alpha', 'remove',
        '-alpha', 'off', generate_displacement_map_tmp
    ]
    subprocess.run(cmd2, check=True)

    # Apply blur to displacement map
    cmd3 = [
        'magick', generate_displacement_map_tmp, '-blur', '0x10', displacement_map
    ]
    subprocess.run(cmd3, check=True)
