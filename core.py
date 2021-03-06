import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pdf2image import convert_from_path
import glob
import os
import shutil
import app
from PyPDF2 import PdfFileReader


def pdf_to_img(dir, filepath):
    # Get file name
    # fname = os.path.split(filepath)[1]

    # Create a temp folder to store extracted images
    temp = dir[0] + '/temp'
    if not os.path.exists(temp): 
        os.mkdir(temp)  
    else:
        remove_temp_folder(dir)
        os.mkdir(temp)
    # except OSError as e:
    #     print("Error: %s" % (e.strerror))

    # Convert PDF pages into images            
    images = convert_from_path(filepath)
    for i in range(len(images)):
        images[i].save(dir[0] + '/' + 'temp/' + dir[1].split('.')[0] + '_' + str(i+1).zfill(4) +'.jpg', 'JPEG')
    
    return glob.glob(dir[0] + '/' + 'temp/*.jpg')

def remove_temp_folder(dir):
    temp = dir[0] + '/temp'
    try:
        shutil.rmtree(temp)
    except OSError as e:
        print("Error : %s" % (e.strerror))

def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0
    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
    key=lambda b:b[1][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)

def detect_lines(img):
    #thresholding the image to a binary image
    thresh,img_bin = cv2.threshold(img,128,255,cv2.THRESH_BINARY |cv2.THRESH_OTSU)
    #inverting the image 
    img_bin = 255-img_bin
    # Length(width) of kernel as 100th of total width
    kernel_len = np.array(img).shape[1]//100
    # Defining a vertical kernel to detect all vertical lines of image 
    ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
    # Defining a horizontal kernel to detect all horizontal lines of image
    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
    # A kernel of 2x2
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    #Use vertical kernel to detect and save the vertical lines in a jpg
    image_1 = cv2.erode(img_bin, ver_kernel, iterations=3)
    vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=3)
    #Use horizontal kernel to detect and save the horizontal lines in a jpg
    image_2 = cv2.erode(img_bin, hor_kernel, iterations=3)
    horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)
    # Combine horizontal and vertical lines in a new third image, with both having same weight.
    img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
    #Eroding and thesholding the image
    img_vh = cv2.erode(~img_vh, kernel, iterations=2)
    thresh, img_vh = cv2.threshold(img_vh,128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    bitxor = cv2.bitwise_xor(img,img_vh)
    bitnot = cv2.bitwise_not(bitxor)
    # Detect contours for following box detection
    contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  
    # Sort all the contours by top to bottom.
    contours, boundingBoxes = sort_contours(contours, method='top-to-bottom')
    return bitnot, contours, boundingBoxes

def get_cells(img, contours, boundingBoxes):
    #Creating a list of heights for all detected boxes
    heights = [boundingBoxes[i][3] for i in range(len(boundingBoxes))]
    #Get mean of heights
    mean = np.mean(heights)
    #Create list box to store all boxes in  
    box = []
    # Get position (x,y), width and height for every contour and show the contour on image
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if (w<1000 and h<500):
            image = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            box.append([x,y,w,h])
    #Creating two lists to define row and column in which cell is located
    row=[]
    column=[]
    j=0
    #Sorting the boxes to their respective row and column
    for i in range(len(box)):
        if(i==0):
            column.append(box[i])
            previous=box[i]
        else:
            if(box[i][1]<=previous[1]+mean/8):
                column.append(box[i])
                previous=box[i]
                if(i==len(box)-1):
                    row.append(column)
            else:
                row.append(column)
                column=[]
                previous = box[i]
                column.append(box[i])
    #calculating maximum number of cells
    countcol = 0
    for i in range(len(row)):
        countcol = len(row[i])
        if countcol > countcol:
            countcol = countcol

    #Retrieving the center of each column
    center = [int(row[i][j][0]+row[i][j][2]/2) for j in range(len(row[i])) if row[0]]
    center=np.array(center)
    center.sort()
    #Regarding the distance to the columns center, the boxes are arranged in respective order
    finalboxes = []
    for i in range(len(row)):
        lis=[]
        for k in range(countcol):
            lis.append([])
        for j in range(len(row[i])):
            diff = abs(center-(row[i][j][0]+row[i][j][2]/4))
            minimum = min(diff)
            indexing = list(diff).index(minimum)
            lis[indexing].append(row[i][j])
        finalboxes.append(lis)
    return row, countcol, finalboxes

def extract_text(dir, save_loc, imgpath, bitnot, row, countcol, finalboxes):
    #from every single image-based cell/box the strings are extracted via pytesseract and stored in a list
    outer=[]
    for i in range(len(finalboxes)):
        for j in range(len(finalboxes[i])):
            # print(f'finalbox[{i}][{j}] == {finalboxes[i][j]}')
            inner=''
            if(len(finalboxes[i][j])==0):
                outer.append(' ')
            else:
                for k in range(len(finalboxes[i][j])):
                    y,x,w,h = finalboxes[i][j][k][0],finalboxes[i][j][k][1], 
                    finalboxes[i][j][k][2],finalboxes[i][j][k][3]
                    finalimg = bitnot[x:x+h, y:y+w]
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
                    border = cv2.copyMakeBorder(finalimg,2,2,2,2,   cv2.BORDER_CONSTANT,value=[255,255])
                    resizing = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    dilation = cv2.dilate(resizing, kernel,iterations=1)
                    erosion = cv2.erode(dilation, kernel,iterations=1)

                    if i==0: #first row: table title 
                        out = pytesseract.image_to_string(erosion, config='-l vie')
                    else:
                        if j==0: #first col: date time
                            out = pytesseract.image_to_string(erosion, 
                            config='-l eng --psm 12')
                        elif j==2 or j==3 or j==4:
                            out = pytesseract.image_to_string(erosion, 
                            config='-l eng -c tessedit_char_whitelist=0123456789,')
                        elif j==5: 
                            out = pytesseract.image_to_string(erosion, 
                            config='-l eng -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                        else:
                            out = pytesseract.image_to_string(erosion)
                    if(len(out)==0):
                        out = pytesseract.image_to_string(erosion, config='--psm 3')
                    inner = inner +" "+ out.replace('\x0c', '')
                outer.append(inner)

    #Creating a dataframe of the generated OCR list
    arr = np.array(outer)
    dataframe = pd.DataFrame(arr.reshape(len(row),countcol))
    # print(dataframe)
    data = dataframe.style.set_properties(align="left")
    # filename = dir[0] + '/' + dir[1].split('.')[0] + '_output.xlsx'
    filename = save_loc + '/' + dir[1].split('.')[0] + '_output.xlsx'
    sheetname = os.path.split(imgpath)[1].split('.')[0].split('_')[1]
    #Converting it in a excel-file
    if os.path.exists(filename):
        with pd.ExcelWriter(filename, mode='a') as writer:  
            data.to_excel(writer, encoding = 'utf-8', sheet_name = sheetname)
    else:
        with pd.ExcelWriter(filename, mode='w') as writer:  
            data.to_excel(writer, encoding = 'utf-8', sheet_name = sheetname) # , index = False
    return os.path.split(filename)[1], sheetname

############### MAIN ###############
def main_convert(lspaths, save_loc):  
    # app = app.App(self) 
    # pagescount = 0 
    # for pdffile in lspaths:
    #     with open(pdffile, "rb") as pdf_file:
    #         pdf_reader = PdfFileReader(pdf_file)
    #         pagescount += pdf_reader.numPages
    # print(pagescount)

    for pdffile in lspaths:
        dir = os.path.split(pdffile)
        print('working on ', dir)
        images = pdf_to_img(dir, pdffile)
        
        for imgpath in sorted(images):
            #read your file
            img = cv2.imread(imgpath,0)
            bitnot, contours, boundingBoxes = detect_lines(img)
            row, countcol, finalboxes       = get_cells(img, contours, boundingBoxes)
            filename, sheetname             = extract_text(dir, save_loc, imgpath, bitnot, row, countcol, finalboxes)
            # app.step(100/pagescount)
            # print('step = ', 100/pagescount)


        remove_temp_folder(dir)
        global done
        done = os.path.split(filename)[1] + ' was saved!\n'
        print(done)
        
        #########NOT WORKING 
        # app = app.App(self)
        # app.convert_tb.config(state='normal')
        # app.convert_tb.insert('end-1c', core.done)
        # app.convert_tb.tag_configure("center", justify="center")
        # app.convert_tb.tag_add("center", 1.0, "end")
        # app.convert_tb.config(state='disabled')


if __name__== "__main__":
    path = glob.glob('/home/anvnt/Documents/bsconverter/PDF-SaoKeNH/*.pdf')
    main_convert(path)
