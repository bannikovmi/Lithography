#########################################################################################
### Imports
#########################################################################################
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

#########################################################################################
### Constants
#########################################################################################
MATRIX_WIDTH = 1920
MATRIX_HEIGHT = 1080
PROJ_WIDTH = 1280
PROJ_HEIGHT = 720

#########################################################################################
### Parse scan params
#########################################################################################
base_path = "/home/litho-pc/litho-venv/Lithography/data/proj_scans" 
scan_params = "0_720_60-0_1280_80-0_256_15"
data_dir = f"{base_path}/{scan_params}"

# Parse scan params from data dir name
x, y, i = scan_params.split("-")
x_start, x_stop, x_step = (int(num) for num in x.split("_"))
y_start, y_stop, y_step = (int(num) for num in y.split("_"))
i_start, i_stop, i_step = (int(num) for num in i.split("_"))

x_len = len(range(x_start, x_stop, x_step))
y_len = len(range(y_start, y_stop, y_step))
i_len = len(range(i_start, i_stop, i_step))

#########################################################################################
### Region of interest calculation
#########################################################################################
x_mat_step = (MATRIX_WIDTH/PROJ_WIDTH)*x_step
y_mat_step = (MATRIX_HEIGHT/PROJ_HEIGHT)*y_step

def get_roi(img, x_proj, y_proj, w=10, h=10):

    # we assume linear translation
    x_mat = (MATRIX_WIDTH/PROJ_WIDTH)*x_proj
    y_mat = (MATRIX_HEIGHT/PROJ_HEIGHT)*y_proj


    # pts1 = np.float32([[x_mat, y_mat], [x_mat+x_mat_step, y_mat], [x_mat, y_mat+y_mat_step]])
    # pts2 = np.float32([[0, 0], [MATRIX_WIDTH, 0], [0, MATRIX_HEIGHT]])
    # affine_matrix = cv.getAffineTransform(pts1, pts2)
    # warped_img = cv.warpAffine(img, affine_matrix, (w, h))

    x_stop = int(x_mat+x_mat_step)
    y_stop = int(y_mat+y_mat_step)

    return img[int(x_mat):x_stop,int(y_mat):y_stop]

#########################################################################################
### Load data
#########################################################################################
data = np.empty((x_len, y_len, i_len))
plt.figure(figsize=(18, 9))

for ind_x, x in enumerate(range(x_start, x_stop, x_step)):
    
    for ind_y, y in enumerate(range(y_start, y_stop, y_step)):

        for ind_i, i in enumerate(range(i_start, i_stop, i_step)):

            path = f"{data_dir}/{x}_{y}_{x+x_step}_{y+y_step}_{i}.png"
            
            # load image, crop to region of interest and calculate mean
            cv_img = cv.imread(path)[::-1, ::-1, 2] # Double reflection and blue channel

            roi = get_roi(cv_img, x, y)
            mean = roi[:, :].mean()

            
            plt.subplot(3, 6, ind_i+1)
            plt.imshow(cv_img)
            plt.title(f"i={i}")
            plt.xticks([])
            plt.yticks([])
            
            print(x, y, i, mean)

            data[ind_x, ind_y, ind_i] = mean

plt.tight_layout()
plt.show()
# print(data)
