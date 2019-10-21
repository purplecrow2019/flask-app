"""This module will serve the api request."""

from config import client
from app import app
from bson.json_util import dumps
from flask import make_response ,request, jsonify
import json
import ast
import imp
import cv2
from skimage import io
import numpy as np
from bson.json_util import dumps



# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client.doubtnut
# Select the collection
collection = db.QuestionLogs
print(collection)

@app.route("/")
def get_initial_response():
    """Welcome message for the API."""
    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Flask API - Doubtnut - OPENCV'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp



@app.route("/blur", methods=['POST'])
def getBlurPercentage():
    try:
        image_url = request.form.get('image_url')
        print(image_url)
        qid = request.form.get('qid')
        print(qid)
        image = io.imread(image_url)
        # print(image)
        blur_value = cv2.Laplacian(image,cv2.CV_64F).var()
        # print('blur value')
        # print(blur_value)
        updated_obj = {}
        if(blur_value < 100):
            updated_obj['is_blurred'] = True
        updated_obj['blur_value'] = blur_value
        print(updated_obj)
        # find_results = collection.find()
        # for i in find_results:
        #     print(i)


        # collection.update({
        #     "qid":int(qid)
        #     },{
        #     "$set":updated_obj
        #     }, upsert = False)

        # # collection.delete_one({"qid":int(qid)})
        # data ={
        #     'isb':True,
        #     'blur':blur_value
        # }

        response_data ={
            "meta": {
                "code": 200,
                "success": True,
                "message": "SUCCESS",
              },
              "data": updated_obj
        }
        
        return jsonify(response_data)
    except:
        return "", 500

@app.route("/textarea" , methods=['POST'])
def getTextAreaRatio():
    try:
        image_url = request.form.get('image_url')
        image = io.imread(image_url)
        # image = cv2.imread('/Users/apple/Desktop/cropped_image.jpg')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9,9), 0)
        thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
        dilate = cv2.dilate(thresh, kernel, iterations=4)
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        total_area = 0
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 100:
                total_area = total_area + area
                x,y,w,h = cv2.boundingRect(c)
                # print(x,y,w,h)
                cv2.rectangle(image, (x, y), (x + w, y + h), (255,255,12), 3)

            
        original_image_height = image.shape[0]
        original_image_width = image.shape[1]
        original_image_area =  (original_image_height)*(original_image_width)
        isCroppingReq = False
        
        area_ratio = (total_area / original_image_area)
        if(area_ratio > 0.6) :
            isCroppingReq = False
        else:
            isCroppingReq = True

        updated_obj ={}
        updated_obj['crop_required'] = isCroppingReq
        updated_obj['text_area_ratio'] = area_ratio


        collection.update({
            "qid":int(qid)
            },{
            "$set":updated_obj
            }, upsert = False)

        data = {
            "crop_required":isCroppingReq,
            "text_area_ratio":area_ratio
        }

        response_data ={
            "meta": {
                "code": 200,
                "success": true,
                "message": "SUCCESS",
              },
              "data": data
        }

        return make_response(jsonify(response_data),200)
    except:
        return "", 500


@app.route('/skew',methods=['POST'])
def detectSkewing():
    try:
        image_url = request.form.get('image_url')
        image = io.imread(image_url)
        # print(image)
        # plt.imshow(image)
        gray = cv2.cvtColor(image , cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        gray = cv2.bitwise_not(gray)
        # plt.imshow(gray)

        thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # plt.imshow(thresh)
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]
        # print(angle)
        box = cv2.boxPoints(cv2.minAreaRect(coords)) 
        box = np.int0(box)
        image_new = cv2.drawContours(image,[box],0,(0,0,255),2)
        # plt.imshow(image_new)
        # print(angle)
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        is_skewed = False
       

        updated_obj = {}
        if(angle != 0):
            updated_obj['is_skewed'] = True
            updated_obj['skew_angle'] = angle
            collection.update({
                "qid":int(qid)
                },{
                "$set":updated_obj
                }, upsert = False)


        data = {
            "is_skewed":is_skewed,
            "skew_angle":angle
        }

        response_data ={
            "meta": {
                "code": 200,
                "success": true,
                "message": "SUCCESS",
              },
              "data": data
        }
     
        return make_response(jsonify(response_data),200)
    except:
        return "", 500


    

    # try:
    #     # Get the value which needs to be updated
    #     try:
    #         # body = ast.literal_eval(json.dumps(request.get_json()))
    #         image_url = request.form.get('image_url')
    #         image = cv2.imread('image_url')
    #         blur_value = cv2.Laplacian(image,cv2.CV_64F).var()
    #         if(blur_value < 100):
    #             return "blur"
    #         else:
    #             return "not blur"
    #         # print(name)
    #         # return "naem"
    #     except:
    #         # Bad request as the request body is not available
    #         # Add message for debugging purpose

    #         return "error", 400

    #     # Updating the user
    #     # records_updated = collection.update_one({"id": int(user_id)}, body)

    #     # Check if resource is updated
    #     if records_updated.modified_count > 0:
    #         # Prepare the response as resource is updated successfully
    #         return "good", 200
    #     else:
    #         # Bad request as the resource is not available to update
    #         # Add message for debugging purpose
    #         return "goog", 404
    # except:
    #     # Error while trying to update the resource
    #     # Add message for debugging purpose
    #     return "err", 500


# @app.route("/api/v1/users/<user_id>", methods=['DELETE'])
# def remove_user(user_id):
#     """
#        Function to remove the user.
#        """
#     try:
#         # Delete the user
#         delete_user = collection.delete_one({"id": int(user_id)})

#         if delete_user.deleted_count > 0 :
#             # Prepare the response
#             return "", 204
#         else:
#             # Resource Not found
#             return "", 404
#     except:
#         # Error while trying to delete the resource
#         # Add message for debugging purpose
#         return "", 500


@app.errorhandler(404)
def page_not_found(e):
  
    message = {
        "err":
            {
                "msg": "This route is currently not supported. Please refer API documentation."
            }
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp
