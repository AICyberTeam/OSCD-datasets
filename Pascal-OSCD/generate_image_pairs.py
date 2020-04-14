# encoding:utf-8
# 1. Get the information of all query images in Pascal VOC dataset and save it to the dict of query_img_class.
# 2. Get the information of all support images in Pascal VOC dataset and save it to the dict of support_img_class,
#    crop all support objects from the query images according to the annotated bounding boxes then save them into disk.
# 3. Generate training/validation/test image pairs by randomly pairing.
import os, sys
import cv2
import copy
import argparse
import xml.etree.ElementTree as ET
import pickle
import random


def get_file(path):
    allfile = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            allfile.append(os.path.join(dirpath, dir))
        for name in filenames:
            if name.find('.xml') == -1:
                continue
            allfile.append(os.path.join(dirpath, name))
    return allfile


def crop_img(img, boxes):
    img_crops = []
    for box in boxes:
        x1, y1, x2, y2 = box[0]
        class_name = box[1]
        img_crop = img[y1:y2, x1:x2, :]
        img_crops.append([img_crop, class_name])
    return img_crops


def get_img_path(xml_path):
    xml_path_cp = xml_path.replace('Annotations', 'JPEGImages')
    return xml_path_cp.replace('.xml', '.jpg')


def save_all_crops(img_crops, file_name, save_dir):
    base_name = os.path.basename(file_name)
    for idx, img_crop in enumerate(img_crops):
        rst_name = os.path.join(save_dir, base_name[:base_name.find('.jpg')] + '_' + str(idx) + base_name[
                                                                                                base_name.find(
                                                                                                    '.jpg'):])
        cv2.imwrite(rst_name, img_crop[0])


def get_all_crop(xml_path):
    rtn_boxes = []
    et = ET.parse(xml_path)
    element = et.getroot()

    element_objs = element.findall('object')
    for obj in element_objs:
        try:
            class_name = obj.find('name').text
            x1 = int(obj.find('bndbox').find('xmin').text)
            y1 = int(obj.find('bndbox').find('ymin').text)
            x2 = int(obj.find('bndbox').find('xmax').text)
            y2 = int(obj.find('bndbox').find('ymax').text)
            rtn_boxes.append([[x1, y1, x2, y2], class_name])
        except Exception as e:
            continue
    return rtn_boxes


def get_target_name(xml_path, all_target_name):
    et = ET.parse(xml_path)
    element = et.getroot()
    element_objs = element.findall('object')

    for obj in element_objs:
        class_name = obj.find('name').text
        if class_name not in all_target_name:
            all_target_name.append(class_name)
        if len(all_target_name) == 20:
            break
    return all_target_name


# This function is to generate training/validation/test image pairs by randomly pairing.
# Here, we just give an example of generating the training image pairs.
def gen_siamese_data(support_img_class_path='./support_img_class.pickle', query_img_class_path='./query_img_class.pickle'):
    with open(support_img_class_path, 'rb') as f:
        support_img_class = pickle.load(f)
    with open(query_img_class_path, 'rb') as f:
        query_img_class = pickle.load(f)
    # We divide all 20 classes with a ratio of 4:1 so that there are 16 seen classes for training/validation,
    # and 4 unseen classes for test.
    train_class_names = ['pottedplant', 'sofa', 'tvmonitor', 'car', 'bottle', 'boat', 'chair', 'person', 'bus', 'train', 'horse',
     'bicycle', 'dog', 'bird', 'motorbike', 'diningtable']
    test_class_names = ['cow', 'sheep', 'cat', 'aeroplane']

    # the number of the selected image pairs for each class
    # for example, the number of training image pairs: 6250 * 16 = 100,000
    num_per_class = 6250
    train_pairs = []
    for index, class_name in enumerate(train_class_names):
        print('Process class {} : {}'.format(index, class_name))
        n = num_per_class
        t = query_img_class[class_name]
        q = support_img_class[class_name]
        if len(t) > 6000:  # to reduce the computation burden
            random.shuffle(t)
            t = t[:6000]
        if len(q) > 6000:
            random.shuffle(q)
            q = q[:6000]
        combs = list(product(t, q))
        random.shuffle(combs)

        for pair in combs[:n]:
            train_pairs.append(pair)

    print('Generate genuine Done')
    print('Save genuine Data')

    with open('./train_pairs.pickle', 'wb') as f:
        pickle.dump(train_pairs, f, protocol=2)


if __name__ == '__main__':
    print('Start job...')
    xml_path = 'path to VOC dataset/VOCdevkit/VOC2012/Annotations'
    save_dir = './SupportImages'  # save the cropped support images

    xmls_path = get_file(xml_path)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # get image filenames { class name：[image filenames...] }
    query_img_class = {}  # query images
    support_img_class = {}  # support images
    all_target_name = []

    # get all class names in this dataset
    for xml_path in xmls_path:
        all_target_name = get_target_name(xml_path, all_target_name)

    for itarget_name in all_target_name:
        target_dir = os.path.join(save_dir, itarget_name)
        # make dir for each class to save the support images
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        query_img_class[itarget_name] = []
        support_img_class[itarget_name] = []

    len_xmls = len(xmls_path)
    train_data = []
    # crop the support objects from the query images according to the annotated bounding boxes,
    # then save them into the corresponding dir
    for index, xml_path in enumerate(xmls_path):
        boxes = get_all_crop(xml_path)
        img_path = get_img_path(xml_path)
        img = cv2.imread(img_path)
        img_crops = crop_img(img, boxes)

        train_data.append([img_path, boxes])

        save_all_crops(img_crops, img_path, save_dir)
        # support image name: 'class name' + '_' + 'num.png'
        base_name = os.path.basename(img_path)
        for idx, img_crop in enumerate(img_crops):
            class_name = img_crop[1]
            support_img_path = os.path.join(save_dir, class_name, base_name[:base_name.find('.jpg')] +
                                            '_' + str(idx) + base_name[base_name.find('.jpg'):])
            cv2.imwrite(support_img_path, img_crop[0])

            # add the information of the support image to support_image_class
            if [support_img_path, class_name] not in support_img_class[class_name]:
                support_img_class[class_name].append([support_img_path, class_name])
            # # add the information of the query image to query_image_class
            if [img_path, boxes] not in query_img_class[class_name]:
                query_img_class[class_name].append([img_path, boxes])

            print('Process {}, percent {}.2f'.format(index, index / float(len_xmls) * 100))

    print('Finished all images, save result...')
    # save support_img_class、query_img_class into disk
    support_img_class_path = './support_img_class.pickle'
    query_img_class_path = './query_img_class.pickle'
    with open(support_img_class_path, 'wb') as f:
        pickle.dump(support_img_class, f, protocol=2)
    with open(query_img_class_path, 'wb') as f:
        pickle.dump(query_img_class, f, protocol=2)
    #  generate training/validation/test image pairs by randomly pairing.
    gen_siamese_data(support_img_class_path, query_img_class_path)