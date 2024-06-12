from pathlib import Path
# settings = {
#   'BASE_PATH': ["/usr/src/web/media/originalUZI/base/download.png"],
#   'IMAGE_NAME_MAX_CHARS': 10,
#   'MAX_IMAGE_BYTES': 1024,
#   'BASE_MODEL_PATH': Path('/usr/src/web/media/nnModel/base/'),
#   'classification': {
#     'all': '/usr/src/web/media/nnModel/base/classUZI/all/resnet.pth',
#     'cross': '/usr/src/web/media/nnModel/base/classUZI/cross/resnet.pth', 
#     'long': '/usr/src/web/media/nnModel/base/classUZI/long/resnet.pth'
#   },
#   'box': {
#     'full': '/usr/src/web/media/nnModel/base/boxUZI/full',
#     'cross': '/usr/src/web/media/nnModel/base/boxUZI/cross', 
#     'long': '/usr/src/web/media/nnModel/base/boxUZI/long'
#   },
#   'segmentation': {
#     'all': [
#       '/usr/src/web/media/nnModel/base/segUZI/all/cascade1.pkl', 
#       '/usr/src/web/media/nnModel/base/segUZI/all/cascade2.pkl'
#       ], 
#     'cross': [
#       '/usr/src/web/media/nnModel/base/segUZI/cross/cascade1.pkl', 
#       '/usr/src/web/media/nnModel/base/segUZI/cross/cascade2.pkl'
#       ], 
#     'long': [
#       '/usr/src/web/media/nnModel/base/segUZI/long/cascade1.pkl', 
#       '/usr/src/web/media/nnModel/base/segUZI/long/cascade2.pkl'
#     ]},
#   'tracking': ['models/tracking_model.pkl'],
# }


settings = {
  'BASE_PATH': ["/usr/src/web/media/originalUZI/base/download.png"],
  'IMAGE_NAME_MAX_CHARS': 10,
  'MAX_IMAGE_BYTES': 1024,
  'BASE_MODEL_PATH': Path('/usr/src/web/media/nnModel/base/'),
  'classification': {
    # 'all': '/usr/src/web/media/nnModel/base/classUZI/all/resnet.zip',
    'cross': '/usr/src/web/media/nnModel/base/classUZI/cross/resnet.zip', 
    'long': '/usr/src/web/media/nnModel/base/classUZI/long/resnet.zip'
  },
  'box': {
    'full': '/usr/src/web/media/nnModel/base/boxUZI/full/box.zip',
    # 'cross': '/usr/src/web/media/nnModel/base/boxUZI/cross/box.zip', 
    # 'long': '/usr/src/web/media/nnModel/base/boxUZI/long/box.zip'
  },
  'segmentation': {
    # 'all': '/usr/src/web/media/nnModel/base/segUZI/all/seg.zip', 
    'cross': '/usr/src/web/media/nnModel/base/segUZI/cross/deeplabv3plus.zip', 
    'long': '/usr/src/web/media/nnModel/base/segUZI/long/deeplabv3plus.zip'
    # 'cross': 'models/cross/deeplabv3plus.pkl', 
    # 'long': 'models/long/deeplabv3plus.pkl'
    },
}
