"""
Process an image file using tesseract.
"""
import os

from .utils import ShellParser

from PIL import Image


class Parser(ShellParser):
    """Extract text from various image file formats using tesseract-ocr"""

    def rotate_ppm_image(self, image_path, angle):
        try:
            image = Image.open(image_path)
            rotated_image = image.rotate(angle, expand=True)
            rotated_image.save(image_path, format='PPM')
        except Exception as e:
            print(f"Err: {e}")

    def extract(self, filename, **kwargs):
    
        #detect rotation
        stdout, _ = self.run(['tesseract', filename, 'stdout', '--psm', '0'])
        rotation_angle = int(stdout.decode("utf-8").split("\n")[2].split(":")[-1].strip())
        if rotation_angle != 0:
            self.rotate_ppm_image(filename, -rotation_angle)

        # if language given as argument, specify language for tesseract to use
        if 'language' in kwargs:
            args = ['tesseract', filename, 'stdout', '-l', kwargs['language']]
        else:
            args = ['tesseract', filename, 'stdout']

        stdout, _ = self.run(args)
        return stdout