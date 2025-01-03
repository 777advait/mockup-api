import subprocess

def create_adjustment_map(template, mask):
    out = 'maps/adjustment_map.jpg'

    # Command to apply mask and create adjustment map
    cmd = [
        'convert', template, '(', '-clone', '0', '-fill', '#f1f1f1', '-colorize', '100', ')',
        mask, '-compose', 'DivideSrc', '-composite', out
    ]
    subprocess.run(cmd, check=True)