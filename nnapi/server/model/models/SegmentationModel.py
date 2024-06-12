from typing import Iterable
import torch
from PIL import Image
from skimage.measure import label as sklabel
from skimage.measure import regionprops
from skimage.transform import resize
from torchvision import transforms as T
from pathlib import Path
import numpy as np
import segmentation_models_pytorch as smp


from server.model.nnmodel import ModelABC, settings
from server.model.loaders.modelPreLoader import ModelPreLoaderABC, ZipModelPreLoader

class SegmentationModel(ModelABC):
    def __init__(self, model_type: str, projection_type:str='full', model_pre_loader:ModelPreLoaderABC=ZipModelPreLoader) -> None:
        self._base_clear()
        self.img_type = None
        self.model_type = model_type
        self.projection_type = projection_type
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        
        print(f'Device: {self.device}')
        self.pre_loader = model_pre_loader(model_type, projection_type)
        base_dir = self.pre_loader.load(settings['segmentation'][self.projection_type])
        self.load(base_dir)

    def _base_clear(self):
        self.rois = []
        self.images = []
        self.result_masks = []
        self.bbox_coordinates = []

    def load(self, path: str) -> None:
        path2 = Path(path)
        weight_c1 = path2 / 'deeplabv3plus.pkl'
        with torch.no_grad():
            self._model = smp.DeepLabV3Plus(
                encoder_name="efficientnet-b6", encoder_weights=None, in_channels=1, classes=1)
            self._model.to(self.device)
            self._model.load_state_dict(torch.load(
                weight_c1, map_location=self.device))
            self._model.eval()


    @staticmethod
    def preprocessing(img: object) -> object:
        img = Image.fromarray(img)
        img = img.convert(mode='L')
        Transform = T.Compose([T.ToTensor()])
        img_tensor = Transform(img)
        img_dtype = img_tensor.dtype
        img_array_fromtensor = (torch.squeeze(img_tensor)).data.cpu().numpy()
        img_array = np.array(img, dtype=np.float32)
        or_shape = img_array.shape
        if or_shape == (735, 975):
            x_cut_min = 130
            x_cut_max = 655
            y_cut_min = 155
            y_cut_max = 700
        elif or_shape == (528, 687):
            x_cut_min = 15
            x_cut_max = 420
            y_cut_min = 40
            y_cut_max = 640
        else:
            value_x = np.mean(img, 1)
            value_y = np.mean(img, 0)
            x_hold_range = list(
                (len(value_x) * np.array([0.24 / 3, 2.2 / 3])).astype(int))
            y_hold_range = list(
                (len(value_y) * np.array([0.8 / 3, 1.8 / 3])).astype(int))
            value_thresold = 5
            x_cut = np.argwhere((value_x <= value_thresold) == True)
            x_cut_min = list(x_cut[x_cut <= x_hold_range[0]])
            if x_cut_min:
                x_cut_min = max(x_cut_min)
            else:
                x_cut_min = 0
            x_cut_max = list(x_cut[x_cut >= x_hold_range[1]])
            if x_cut_max:
                x_cut_max = min(x_cut_max)
            else:
                x_cut_max = or_shape[0]
            y_cut = np.argwhere((value_y <= value_thresold) == True)
            y_cut_min = list(y_cut[y_cut <= y_hold_range[0]])
            if y_cut_min:
                y_cut_min = max(y_cut_min)
            else:
                y_cut_min = 0
            y_cut_max = list(y_cut[y_cut >= y_hold_range[1]])
            if y_cut_max:
                y_cut_max = min(y_cut_max)
            else:
                y_cut_max = or_shape[1]
        cut_image = img_array_fromtensor[x_cut_min:x_cut_max,
                                         y_cut_min:y_cut_max]
        cut_image_orshape = cut_image.shape
        cut_image = resize(cut_image, (256, 256), order=3)
        cut_image_tensor = torch.tensor(data=cut_image, dtype=img_dtype)
        return [cut_image_tensor, cut_image_orshape, or_shape, [x_cut_min, x_cut_max, y_cut_min, y_cut_max]]

    @staticmethod
    def get_connect_components(bw_img: object) -> list:
        if np.sum(bw_img) == 0:
            return []
        labeled_img, num = sklabel(bw_img, connectivity=1, background=0, return_num=True)
        return [(labeled_img == i + 1).astype(int) for i in range(num)]

    @staticmethod
    def preprocessing2(mask_c1_array_biggest: object) -> list:
        if np.sum(mask_c1_array_biggest) == 0:
            minr, minc, maxr, maxc = [0, 0, 256, 256]
        else:
            region = regionprops(mask_c1_array_biggest)[0]
            minr, minc, maxr, maxc = region.bbox
        dim1_center, dim2_center = [(maxr + minr) // 2, (maxc + minc) // 2]
        max_length = max(maxr - minr, maxc - minc)
        max_lengthl = int((256 / 256) * 80)
        preprocess1 = int((256 / 256) * 19)
        pp22 = int((256 / 256) * 31)
        if max_length > max_lengthl:
            ex_pixel = preprocess1 + max_length // 2
        else:
            ex_pixel = pp22 + max_length // 2
        dim1_cut_min = dim1_center - ex_pixel
        dim1_cut_max = dim1_center + ex_pixel
        dim2_cut_min = dim2_center - ex_pixel
        dim2_cut_max = dim2_center + ex_pixel
        if dim1_cut_min < 0:
            dim1_cut_min = 0
        if dim2_cut_min < 0:
            dim2_cut_min = 0
        if dim1_cut_max > 256:
            dim1_cut_max = 256
        if dim2_cut_max > 256:
            dim2_cut_max = 256
        return [dim1_cut_min, dim1_cut_max, dim2_cut_min, dim2_cut_max]

    @staticmethod
    def get_bbox(img: object) -> object:
        c = np.where(img != 0)
        # return [np.max(c[1]), np.max(c[0]), np.min(c[1]), np.min(c[0])]
        return [np.min(c[1]), np.min(c[0]), np.max(c[1]), np.max(c[0])]

    def predict(self, images: Iterable) -> object:
        self._base_clear()
        with torch.no_grad():
            for index, im in enumerate(images):
                img, cut_image_orshape, or_shape, location = self.preprocessing(im)
                self.img_type = img.dtype
                img = torch.unsqueeze(img, 0)
                img = torch.unsqueeze(img, 0)
                img = img.to(self.device)
                img_array = (torch.squeeze(img)).data.cpu().numpy()

                mask_c1 = self._model(img)
                mask_c1 = torch.sigmoid(mask_c1)
                mask_c1_array = (torch.squeeze(
                    mask_c1)).data.cpu().numpy()
                mask_c1_array = (mask_c1_array > 0.5)
                mask_c1_array = mask_c1_array.astype(np.float32)
                nodules = self.get_connect_components(mask_c1_array.astype(int))

                new_nodules = []
                coordinates = []
                for nd in nodules:
                    dim1_cut_min, dim1_cut_max, dim2_cut_min, dim2_cut_max = self.preprocessing2(nd)
                    img_array_roi = img_array[dim1_cut_min:dim1_cut_max, dim2_cut_min:dim2_cut_max]
                    new_nodules.append(img_array_roi)
                    n1_array = nd.astype(np.float32)
                    f1_mask = np.zeros(shape=or_shape, dtype=mask_c1_array.dtype)
                    n1_array = resize(n1_array, cut_image_orshape, order=1)
                    f1_mask[location[0]:location[1], location[2]:location[3]] = n1_array
                    f1_mask = (f1_mask > 0.5)
                    f1_mask = f1_mask.astype(np.float32)
                    cs = self.get_bbox(f1_mask)
                    coordinates.append(cs)
                self.rois.append(new_nodules)
                self.bbox_coordinates.append(coordinates)

                final_mask = np.zeros(shape=or_shape, dtype=mask_c1_array.dtype)
                mask_c1_array = resize(mask_c1_array, cut_image_orshape, order=1)
                final_mask[location[0]:location[1], location[2]:location[3]] = mask_c1_array
                final_mask = (final_mask > 0.5)
                final_mask = np.where(final_mask > 0, 255, 0).astype(np.uint8)
                self.result_masks.append(final_mask)
        self.result_masks = np.array(self.result_masks)
        return self.result_masks
