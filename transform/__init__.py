import azure.functions as func
import logging
import base64
import numpy as np
import cv2

def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Python Transform Image HTTP trigger function is processing a request.')

    # parse json body
    req_body = req.get_json()
    req_image = req_body.get('image')
    req_points = req_body.get('points')

    # read image from base64 string
    s_image = readb64(req_image)

    # read the corner points
    s_pts = np.array([
        [req_points['p1']['x'], req_points['p1']['y']],
        [req_points['p2']['x'], req_points['p2']['y']],
        [req_points['p3']['x'], req_points['p3']['y']],
        [req_points['p4']['x'], req_points['p4']['y']]], np.int32)

    # sort the points clockwise
    s_pts = order_points(s_pts)
    t_pts, maxWidth, maxHeight = get_target_points(s_pts)

    # calculate transform
    M = cv2.getPerspectiveTransform(s_pts,t_pts)

    # transform
    t_image = cv2.warpPerspective(s_image, M, (maxWidth, maxHeight))

    # encode image as JPG
    _, img_encoded = cv2.imencode('.jpg', t_image)

    # convert image to base64 string
    t_image_b64 = base64.b64encode(img_encoded).decode('utf-8')

    # send response
    return func.HttpResponse(f"{{\"image\":\"{t_image_b64}\"}}", status_code=200, mimetype="application/json")


def readb64(str):
   nparr = np.fromstring(base64.b64decode(str), np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   return img

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")

	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]

	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return rect

def get_target_points(pts):
    # obtain a consistent order of the points and unpack them
    # individually
    (tl, tr, br, bl) = pts

    # compute the width of the new image, which will be the
    # minimum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = min(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # minimum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = min(int(heightA), int(heightB))  

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    return dst, maxWidth, maxHeight