from lightning_map import convert_images as convert_lightning_map
from displacement_map import convert_images as convert_displacement_map
from adjustment_map import create_adjustment_map



def create_maps(template, mask):
    convert_lightning_map(template, mask)
    convert_displacement_map(template, mask)
    create_adjustment_map(template, mask)