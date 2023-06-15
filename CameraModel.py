import cv2
import logging
import numpy as np

class CameraModel:

    def __init__(self,newcameramtx,roi,objpoints,real_points_array,mtx,dist,rvecs,tvecs, photos, chessboard_size):
        self.newcameramtx = newcameramtx
        self.roi = roi
        self.mtx = mtx
        self.dist = dist
        self.objpoints = objpoints
        self.real_points_array = real_points_array
        self.rvecs = rvecs
        self.tvecs = tvecs
        self.photos = photos
        self.chessboard_size = chessboard_size
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def mean_error_for_images_used_for_calibration(self):
        mean_error = 0
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], self.rvecs[i], self.tvecs[i], self.mtx, self.dist)
        error = cv2.norm(self.real_points_array[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        mean_error += error
        total_error = mean_error/len(self.objpoints)
        print( "total error: {}".format(mean_error/len(self.objpoints)))
        return total_error

    def undistort_img(self, img):
        h, w = img.shape[:2]
        mapx, mapy = cv2.initUndistortRectifyMap(self.mtx, self.dist, None, self.newcameramtx, (w, h), 5)
        dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
        x, y, w, h = self.roi
        dst = dst[y:y + h, x:x + w]
        return dst

def calibrate_camera(photos, chessboard_size):
    photos = photos
    chessboard_size = chessboard_size
    # Statistic arrays and constants
    logging.info("Create statistic arrays and constants")
    objpoints = []
    points_array = []
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    logging.info("Starting looping in images")
    for img in photos:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(img_gray, chessboard_size, None)
        logging.info(ret if 'Chessboard Corners has been found' else 'None chessboard Corners has been found')

        if ret:
            objpoints.append(objp)
            cornersSubPix = cv2.cornerSubPix(img_gray,
                                        corners,
                                        (11, 11),
                                        (-1, -1),
                                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            points_array.append(cornersSubPix)
            cv2.drawChessboardCorners(img, chessboard_size, cornersSubPix, ret)

    if len(points_array) > 0:
        logging.info("Start camera calibration")
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, points_array, img_gray.shape[::-1], None, None)
        with open('parameters.txt','w') as file:
            file.write("RET" + '\n' +str(ret) + '\n' + "MTX" + '\n' +str(mtx) + '\n' + "DIST" + '\n' + str(dist) + '\n' + 'RVECS' + '\n' + str(rvecs) + '\n' + "TVECS" + '\n' + str(tvecs))
            file.close()
        print("Successful calibration")
    else:
        print("There is no points. ERROR.")

    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 0, (w,h))


    return CameraModel(newcameramtx,roi,objpoints,points_array,mtx,dist,rvecs,tvecs, photos, chessboard_size)