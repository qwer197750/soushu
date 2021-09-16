import os

from googlenet.googleNet import predict
from googlenet.cut_image import split
from googlenet.cut_image import read_label_from_cvs
import warnings


def identify(img_path):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        imgs = split(img_path)
        codes = predict(imgs)
        return ''.join(codes).strip()


def check():
    labels = read_label_from_cvs(r'C:\Users\qwer1\Desktop\label.csv')
    n = 0
    i = 0
    for key in labels.keys():
        file_name = 'code_{:}.png'.format(key)
        if len(labels[key].strip()) != 4:
            continue
        img_path = '../img'
        code = identify(os.path.join(img_path, file_name))
        n += 1
        if code.strip().upper() != labels[key].strip().upper():
            print('{:} {:} {:}'.format(file_name, labels[key].strip().upper(), code.strip().upper()))
            i += 1
    print('{:}/{:}'.format(i, n))


if __name__ == '__main__':
    # print(identify('../img/code_1501.png'))
    check()