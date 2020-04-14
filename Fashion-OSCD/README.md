## Introduction
Fashion-OSCD is a dataset for one-shot conditional object detection, which is constructed by randomly scaling and embedding samples of Fashion-MNIST dataset into a larger image.

We make each image contain as much as 3 objects with multiple scales and aspect ratios. 7 classes are randomly selected as seen classes for training/validation, the other 3 unseen classes for test. Overall, we generate 8000 training, 8000 validation and 6999 test images. 

The building process is shown below.

![fashionOSCDpipeline](F:\ComparsionNet\NC-修改\最终版相关材料\数据集公开\Fashion-OSCD\fashionOSCDpipeline.png) 

## Download

This dataset can be downloaded from:

OneDrive: https://1drv.ms/u/s!AgYiu2IzGlVAiVYmyr0fN4PSUeYX?e=jKZgdm

BaidiWangpan: https://pan.baidu.com/s/1Q1l9o4UFRYlAHvN-c-h-7Q  password: 0k3t 

The Fashion-MNIST dataset can be downloaded from  https://github.com/zalandoresearch/fashion-mnist#get-the-data

## Building dataset

Generate image pairs by following the example given in generate_image_pairs.py.

## References
[fashion-mnist](https://github.com/zalandoresearch/fashion-mnist)

