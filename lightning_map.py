import subprocess


def convert_images(template, mask):
    normalized_template_map_tmp = 'mpcs/normalized_template_map_tmp.mpc'
    brightness_delta = 30

    # if folders do not exist, create them
    subprocess.run(['mkdir', '-p', 'mpcs'], check=True)
    subprocess.run(['mkdir', '-p', 'maps'], check=True)

    generate_lighting_map_tmp = 'mpcs/generate_lighting_map_tmp.mpc'
    lighting_map = 'maps/lighting_map.png'

    # Execute the first convert command
    cmd1 = [
        'magick', template, mask, '-alpha', 'off', '-colorspace', 'gray',
        '-compose', 'CopyOpacity', '-composite', normalized_template_map_tmp
    ]
    subprocess.run(cmd1, check=True)

    # Execute the second convert command
    cmd2 = [
        'magick', normalized_template_map_tmp, '-evaluate', 'subtract',
        f'{brightness_delta}%', '-background', 'grey50', '-alpha', 'remove',
        '-alpha', 'off', generate_lighting_map_tmp
    ]
    subprocess.run(cmd2, check=True)

    # Execute the third convert command
    cmd3 = [
        'magick', generate_lighting_map_tmp, '(', '-clone', '0', '-fill',
        'grey50', '-colorize', '100', ')', '-compose', 'lighten', '-composite',
        lighting_map
    ]
    subprocess.run(cmd3, check=True)
