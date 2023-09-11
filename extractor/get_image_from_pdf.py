import fitz
import os
from PIL import Image

def readPDF(filePath, outputPath):
    pdf_file = fitz.open(filePath)
    page_nums = len(pdf_file)

    # Create empty list to store images information
    images_list = []

    # Extract all images information from each page
    for page_num in range(page_nums):
        page_content = pdf_file[page_num]
        images_list.extend(page_content.get_images())

    # Raise error if PDF has no images
    if len(images_list) == 0:
        raise ValueError(f'No images found in {filePath}')

    # Save all the extracted images
    for i, image in enumerate(images_list, start=1):
        # Extract the image object number
        xref = image[0]
        # Extract image
        base_image = pdf_file.extract_image(xref)
        # Store image bytes
        image_bytes = base_image['image']
        # Store image extension
        image_ext = base_image['ext']
        # Generate image file name
        image_name = str(i) + '.' + image_ext
        # Save image
        with open(os.path.join(outputPath, image_name), 'wb') as image_file:
            image_file.write(image_bytes)
            image_file.close()

if __name__ == '__main__':
    readPDF(
        '/Users/luoyu/PycharmProjects/protoKG/sampleOne/pdf/acs.joc.8b02978.pdf', 'images/')