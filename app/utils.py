# Utils for preprocessing data
import tensorflow as tf
import googleapiclient.discovery
from google.api_core.client_options import ClientOptions

base_classes = [
    'chicken_curry',
    'chicken_wings',
    'fried_rice',
    'grilled_salmon',
    'hamburger',
    'ice_cream',
    'pizza',
    'ramen',
    'steak',
    'sushi'
]

classes_and_models = {
    "model_1": {
        "classes": base_classes,
        "model_name": "efficientnet_model_1_10_classes"
    },
    "model_2": {
        "classes": sorted(base_classes + ["donut"]),
        "model_name": "efficientnet_model_2_11_classes"
    },
    "model_3": {
        "classes": sorted(base_classes + ["donut", "not_food"]),
        "model_name": "efficientnet_model_3_12_classes"
    }
}

def predict_json(project, region, model, instances, version=None):
    """Send json data to a deployed model for prediction.
    """

    # Create the ML Engine service object
    prefix = "{}-ml".format(region) if region else "ml"
    api_endpoint = "https://{}.googleapis.com".format(prefix)
    client_options = ClientOptions(api_endpoint=api_endpoint)

    # Setup model path
    model_path = "projects/{}/models/{}".format(project, model)
    if version is not None:
        model_path += "/versions/{}".format(version)

    # Create ML engine resource endpoint and input data
    ml_resource = googleapiclient.discovery.build(
        "ml", "v1", cache_discovery=False, client_options=client_options).projects()
    instances_list = instances.numpy().tolist() # turn input into list (ML Engine wants JSON)
    
    input_data_json = {"signature_name": "serving_default",
                       "instances": instances_list} 

    request = ml_resource.predict(name=model_path, body=input_data_json)
    response = request.execute()


    if "error" in response:
        raise RuntimeError(response["error"])

    return response["predictions"]

def load_and_prep_image(filename, img_shape=224, rescale=False):
  """
  Reads in an image from filename, turns it into a tensor and reshapes into
  (224, 224, 3).
  """
  # Decode it into a tensor
  img = tf.io.decode_image(filename, channels=3)
  
  # Resize the image
  img = tf.image.resize(img, [img_shape, img_shape])
  
  # Rescale the image (get all values between 0 and 1)
  if rescale:
      return img/255.
  else:
      return img

def update_logger(image, model_used, pred_class, pred_conf, correct=False, user_label=None):
    """
    Function for tracking feedback given in app, updates and returns 
    logger dictionary.
    """
    logger = {
        "image": image,
        "model_used": model_used,
        "pred_class": pred_class,
        "pred_conf": pred_conf,
        "correct": correct,
        "user_label": user_label
    }   
    return logger
