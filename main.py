from ocr_tamil.ocr import OCR
import pandas as pd
import logging
import json
import os
import re
from os.path import splitext
import cv2
# import fitz
import pandas as pd
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# local
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

# from firsppage import process_pdf_collection

coordinates_dict = {(38, 77, 557, 288): 1, (566, 77, 1084, 288): 2, (1095, 77, 1612, 287): 3, (38, 298, 557, 508): 4,
                    (566, 298, 1084, 508): 5, (1094, 298, 1613, 508): 6, (38, 518, 557, 728): 7,
                    (566, 518, 1084, 728): 8,
                    (1094, 518, 1613, 728): 9, (38, 738, 557, 948): 10, (566, 738, 1085, 948): 11,
                    (1094, 738, 1613, 948): 12,
                    (38, 959, 557, 1169): 13, (566, 959, 1085, 1169): 14, (1094, 959, 1613, 1169): 15,
                    (38, 1179, 557, 1389): 16,
                    (566, 1179, 1084, 1389): 17, (1094, 1179, 1613, 1389): 18, (38, 1399, 557, 1609): 19,
                    (566, 1399, 1085, 1609): 20,
                    (1094, 1400, 1613, 1609): 21, (38, 1619, 557, 1830): 22, (566, 1619, 1084, 1830): 23,
                    (1095, 1620, 1612, 1830): 24,
                    (38, 1839, 557, 2050): 25, (566, 1839, 1084, 2050): 26, (1095, 1840, 1613, 2050): 27,
                    (38, 2060, 557, 2271): 28,
                    (566, 2060, 1084, 2271): 29, (1095, 2060, 1612, 2270): 30}

coordinates = [(38, 77, 557, 288), (566, 77, 1084, 288), (1095, 77, 1612, 287), (38, 298, 557, 508),
               (566, 298, 1084, 508),
               (1094, 298, 1613, 508), (38, 518, 557, 728), (566, 518, 1084, 728), (1094, 518, 1613, 728),
               (38, 738, 557, 948),
               (566, 738, 1085, 948), (1094, 738, 1613, 948), (38, 959, 557, 1169), (566, 959, 1085, 1169),
               (1094, 959, 1613, 1169),
               (38, 1179, 557, 1389), (566, 1179, 1084, 1389), (1094, 1179, 1613, 1389), (38, 1399, 557, 1609),
               (566, 1399, 1085, 1609),
               (1094, 1400, 1613, 1609), (38, 1619, 557, 1830), (566, 1619, 1084, 1830), (1095, 1620, 1612, 1830),
               (38, 1839, 557, 2050),
               (566, 1839, 1084, 2050), (1095, 1840, 1613, 2050), (38, 2060, 557, 2271), (566, 2060, 1084, 2271),
               (1095, 2060, 1612, 2270)]


# ***Function for pdf pages to image conversion***

def convert_pdf_to_images(pdf_paths, output_folder):
    try:
        for pdf_path in pdf_paths:
            pdf_filename = os.path.basename(pdf_path)
            pdf_name = os.path.splitext(pdf_filename)[0]
            pdf_output_folder = os.path.join(output_folder, pdf_name)

            # Create output folder for this PDF if it doesn't exist
            if not os.path.exists(pdf_output_folder):
                os.makedirs(pdf_output_folder)

            try:
                images = convert_from_path(pdf_path)
            except Exception as e:
                print(f'Error converting PDF "{pdf_path}": {e}')
                continue

            for i, image in enumerate(images, start=1):
                # Adjust the starting page number to 1 (not 0)
                image_filename = f'{str(i).zfill(2)}.jpg'
                image_path = os.path.join(pdf_output_folder, image_filename)
                image.save(image_path, 'JPEG')
                print(f'Saved {image_path}')

            print(f'PDF pages from "{pdf_path}" successfully converted to images and saved in: {pdf_output_folder}')

    except Exception as e:
        print(f'Error: {e}')


pdfs_collection_folder = 'tamil_pdf_collections'
output_folder = 'tamil_pdf_images_folder'
pdf_paths = [os.path.join(pdfs_collection_folder, filename) for filename in os.listdir(pdfs_collection_folder) if
             filename.endswith('.pdf')]

convert_pdf_to_images(pdf_paths, output_folder)


# ***Function for Cropping***

def crop_and_save_images(input_for_individual, coordinates, coordinates_dict, output_for_individual):
    try:
        if not os.path.exists(output_for_individual):
            os.makedirs(output_for_individual)

        images_to_skip = 3  # Number of images to skip

        for root, dirs, files in os.walk(input_for_individual):
            for dir in dirs:
                input_folder_path = os.path.join(input_for_individual, dir)
                output_folder_path = os.path.join(output_for_individual, dir)
                if not os.path.exists(output_folder_path):
                    os.makedirs(output_folder_path)

                counter = 1
                for filename in sorted(os.listdir(input_folder_path)):
                    if counter > images_to_skip:
                        image_path = os.path.join(input_folder_path, filename)
                        image = cv2.imread(image_path)
                        page_number = str(os.path.splitext(filename)[0])

                        for coord in coordinates:
                            x1, y1, x2, y2 = coord
                            cropped_image = image[y1:y2, x1:x2]
                            if coord in coordinates_dict.keys():
                                page_no = coordinates_dict[coord]
                                output_filename = f"pdf{dir}_{page_number}_{str(page_no).zfill(2)}.jpg"
                                output_path = os.path.join(output_folder_path, output_filename)
                                cv2.imwrite(output_path, cropped_image)
                                print(f'Saved {output_path}')
                    counter += 1
        print('PDF pages  successfully cropped  and saved')

    except Exception as e:
        print(f'Error cropping images: {e}')


input_for_crop = "tamil_pdf_images_folder"
output_of_crop = "tamil_cropped_images"


# crop_and_save_images(input_for_crop, coordinates, coordinates_dict, output_of_crop)


# ***Function for extraction***


def extract_text_from_images_in_path(images_path, output_folder):
    try:
        ocr = OCR(detect=True)
        os.makedirs(output_folder, exist_ok=True)

        # Iterate through all subdirectories using os.walk()
        for root, dirs, files in os.walk(images_path):
            for directory in dirs:  # Correct variable name here
                input_folder_path = os.path.join(images_path, directory)
                output_folder_path = os.path.join(output_folder, directory)
                if not os.path.exists(output_folder_path):
                    os.makedirs(output_folder_path)

                for filename in os.listdir(input_folder_path):
                    if filename.endswith('.jpg'):
                        image_path = os.path.join(input_folder_path, filename)
                        try:
                            extracted_text = ocr.predict(image_path)
                            print(extracted_text)
                            output_file_path = os.path.join(output_folder_path, f"{os.path.splitext(filename)[0]}.txt")
                            with open(output_file_path, "w", encoding="utf-8") as text_file:
                                text_file.write(extracted_text)
                            print(output_file_path)
                            # text_extracter(extracted_text)
                        except Exception as e:
                            logger.info(image_path)
                            print(e)
        print("converted text successfully")

    except Exception as e:
        print(f'Error: {e}')


# Example usage:
images_path = "tamil_cropped_images"
output_folder = "tamil_extracted_data"


# extract_text_from_images_in_path(images_path, output_folder)


def text_extracter(extracted_folder):
    data_by_subfolder = {}  # Dictionary to store extracted data by subfolder
    result_list = []
    count = 0
    for root, dirs, files in os.walk(extracted_folder):
        for subfolder in dirs:
            subfolder_path = os.path.join(root, subfolder)
            subfolder_data = []  # List to store extracted data from current subfolder
            for filename in os.listdir(subfolder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(subfolder_path, filename)
                    with open(file_path, 'r', encoding="utf-8") as file:
                        extracted_text = file.read()

                    if extracted_text.strip() == '':
                        continue

                    data_dict = {}
                    # global count
                    count += 1
                    data_dict["எண்"] = count
                    detail = extracted_text.split()
                    print(detail)

                    for i, word in enumerate(detail):
                        if word.startswith(('FM', 'ZB')):
                            data_dict["வாக்காளர் எண்"] = word
                            break

                    if "கணவர" in detail:
                        data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("கணவர")])
                        data_dict["Relative"] = "கணவர்"
                        data_dict["உறவுப் பெயர்"] = ''.join(detail[detail.index("கணவர") + 2:detail.index("வீட்டு")])
                    if "கணவர்" in detail:
                        data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("கணவர்")])
                        data_dict["உறவு"] = "கணவர்"
                        data_dict["உறவுப் பெயர்"] = ''.join(
                            detail[
                            detail.index("கணவர்") + 2:detail.index("வீட்டு")]) if "வீட்டு" in detail else ''.join(
                            detail[detail.index("கணவர்") + 2:detail.index("எண்")])

                    if "தந்தையின்" in detail:
                        data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("தந்தையின்")])
                        data_dict["உறவு"] = "தந்தை"
                        if "வீட்டு" in detail:
                            data_dict["உறவுப் பெயர்"] = ''.join(
                                detail[detail.index("தந்தையின்") + 2:detail.index("வீட்டு")])
                        else:
                            data_dict["உறவுப் பெயர்"] = ''.join(detail[detail.index("தந்தையின்") + 2:])
                    elif "தந்தையின்னிபெ" in detail:
                        data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("தந்தையின்னிபெ")])
                        data_dict["உறவு"] = "தந்தை"
                        if "வீட்டு" in detail:
                            data_dict["உறவுப் பெயர்"] = ''.join(
                                detail[detail.index("தந்தையின்னிபெ") + 2:detail.index("வீட்டு")])
                        else:
                            data_dict["உறவுப் பெயர்"] = ''.join(detail[detail.index("தந்தையின்னிபெ") + 2:])

                    if "தந்தையின்" in detail and "எண்" in detail:
                        data_dict["பெயர்"] = ''.join(detail[detail.index("பெயர்") + 1:detail.index("தந்தையின்")])
                        data_dict["உறவு"] = "தந்தை"
                        data_dict["உறவுப் பெயர்"] = ''.join(
                            detail[
                            detail.index("தந்தையின்") + 2:detail.index("வீட்டு")]) if "வீட்டு" in detail else ''.join(
                            detail[detail.index("தந்தையின்") + 2:detail.index("எண்")])

                    # if "வீட்டு" in detail:
                    #     data_dict["வீட்டு எண்"] = ''.join(detail[detail.index("எண்") + 1:detail.index("Photo")])
                    if "எண்" in detail:
                        if "Photo" in detail:
                            data_dict["வீட்டு எண்"] = ''.join(detail[detail.index("எண்") + 1:detail.index("Photo")])
                        else:
                            # If "Photo" is not found, take all elements after "எண்"
                            data_dict["வீட்டு எண்"] = ''.join(detail[detail.index("எண்") + 1:])

                    if "available" in detail:
                        data_dict["பாலினம்"] = ''.join(detail[detail.index("available") - 1])
                    if "வயது" in detail:
                        if "பாலினம்" in detail:
                            data_dict["வயது"] = ''.join(detail[detail.index("வயது") + 1:detail.index("பாலினம்")])
                        else:
                            # If "பாலினம்" is not found, take all elements after "வயது"
                            data_dict["வயது"] = ''.join(detail[detail.index("வயது") + 1:])

                    print(data_dict)
                    if bool(data_dict):
                        result_list.append(data_dict)
                        subfolder_data.append(data_dict)

            data_by_subfolder[subfolder] = subfolder_data
    return data_by_subfolder


extracted_folder = "tamil_extracted_data"
data_by_subfolder = text_extracter(extracted_folder)
for subfolder, extracted_data_list in data_by_subfolder.items():
    df = pd.DataFrame(extracted_data_list)
    excel_folder = "excel_data"
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    excel_file = f'{excel_folder}_{subfolder}.xlsx'
    df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"Excel data saved to '{excel_file}'")