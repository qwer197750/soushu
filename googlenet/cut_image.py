import random
import traceback
import csv
import numpy as np
from PIL import Image
import os


lb = '02346789bcefghjkmprtvwxy'


# 利用裂变的思想，在一个二值矩阵中，找到一个节点数最多的形状（也被称为最大形状）
# 形状指的是矩阵中一些点的集合（这些点都是true，且他们直接是连通的，且矩阵中其它点和这个集合不连通）
# 连通指的是两个点，他们直接存在上下左右、左上右上、左下右下的关系，即称为连通
# 裂变指的是将整个矩阵中所有的true点放到一个待定形状中。这个形状一定包含最大形状
# 然后从待定形状中，找出构成边界的四个点，即含有max_x,max_y,min_x,min_y的四个true点
# 接着从这四个点出发找出这四个点的形状，将这些形状从待定形状中裂解出去
# 重复上述过程，直至裂解后的待定形状小于已知的最大形状，那么已知最大形状为最大形状
class Form():
    def __init__(self):
        # 形状的位置集合
        self.array = None
        self.num = 0
        self.ps = []
        self.max_x = None
        self.max_y = None
        self.min_x = None
        self.min_y = None

    # 在一个待定形状中，从指定x，y的点出发，寻找所有的连通点，构成形状
    def init_form_from_ndf(self, form, x, y):
        self.array = form.array
        assert [x, y] in form.ps
        self.ps = [[x, y]]
        form.ps.remove([x, y])
        increase = [-1, 0, 1]
        for p in self.ps:
            [x, y] = p
            for x_ir in increase:
                for y_ir in increase:
                    if x_ir == 0 and y_ir == 0:
                        continue
                    if [x + x_ir, y + y_ir] in form.ps and [x + x_ir, y + y_ir] not in self.ps:
                        self.ps.append([x + x_ir, y + y_ir])
                        form.ps.remove([x + x_ir, y + y_ir])

        self.re_num()
        form.re_num()

    # 在一个矩阵中，找到所有的true点，构成一个待定形状，以便裂解
    def init_no_determined_form(self, array):
        self.array = array
        self.ps = np.transpose(np.nonzero(array)).tolist()
        self.re_num()

    def re_num(self):
        self.num = len(self.ps)
        if self.num <= 0:
            self.max_y = 0
            self.max_x = 0
            self.min_x = 0
            self.min_y = 0
            return
        self.min_x, self.min_y = np.min(np.asarray(self.ps), axis=0)
        self.max_x, self.max_y = np.max(np.asarray(self.ps), axis=0)

    # 裂解待定形状
    def fission(self):
        fs = []
        max_n = 0
        max_form = None
        while max_n < self.num:
            [x, y] = self.ps[0]
            form = Form()
            form.init_form_from_ndf(self, x, y)
            fs.append(form)
            if max_n < form.num:
                max_n = form.num
                max_form = form
        return max_form


def cut(img_path):
    img = Image.open(img_path).convert("1")
    width, height = img.size
    l = 1/32
    fs = []
    array = np.asarray(img)
    for i in range(4):
        x_b = i * (1/4) - l
        x_b = x_b if x_b >= 0 else 0
        x_b = int(x_b * width)
        x_e = (i+1) * (1/4) + l
        x_e = x_e if x_e <= 1 else 1
        x_e = int(x_e * width)
        # y_b, y_e = max_position(array[:, x_b:x_e])

        form = Form()
        form.init_no_determined_form(array[:, x_b:x_e])
        max_form = form.fission()
        fs.append([max_form, x_b, x_e])
    i = 0
    res = []
    w, h = array.shape
    for f in fs:
        bk = np.zeros([w+5, h+5], dtype=np.bool)
        form, x_b, x_e = f
        for p in form.ps:
            x, y = p
            bk[x+2, x_b+y+2] = array[x, x_b+y]
        res.append(Image.fromarray(bk[:, x_b:x_e+5]))
    return res


def to_bool(array, p):
    sub_array = array[p.min_y:p.max_y + 1, p.min_x:p.max_x + 1, p.k].copy()
    sub_array[sub_array > p.color] = False
    sub_array[sub_array < p.color] = False
    sub_array = np.array(sub_array, dtype=np.bool)
    return sub_array


def add_arrays(array, w, h, num):
    array = array.copy()
    if h > len(array):
        sy = (h-len(array))//2
        by = h - sy - len(array)
        if sy > 0:
            array = np.vstack((np.ones([sy, len(array[0])])*num, array))
        if by > 0:
            array = np.vstack((array, np.ones([by, len(array[0])])*num))
    if w > len(array[0]):
        lx = (w - len(array[0]))//2
        rx = w - lx - len(array[0])
        if lx > 0:
            array = np.hstack((np.ones([h, lx])*num, array))
        if rx > 0:
            array = np.hstack((array, np.ones([h, rx])*num))
    return array.astype(dtype=np.bool)


def not_bool(array):
    array = ~array
    return array


def test_top12(top12, array):
    bs = []
    for p in top12:
        bs.append(to_bool(array, p))
    return bs


class Point():
    @classmethod
    def push(cls, a):
        pass

    def __init__(self, x, y, color=-1, k=-1):
        self.max_x = x
        self.max_y = y
        self.min_x = 10000
        self.min_y = 10000
        self.n = 0
        self.color = color
        self.k = k

    def update_XY(self, x, y):
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)
        self.min_x = min(self.min_x, x)
        self.min_y = min(self.min_y, y)
        self.n += 1

    def similar(self, b):
        sx = self.max_x - self.min_x
        bx = b.max_x - b.min_x
        # 如果二者在x轴上不相交，则相似度为0
        if (self.max_x - b.min_x)*(b.max_x - self.min_x) <= 0:
            return 0
        else:
            a = min(abs(self.max_x - b.min_x), abs(b.max_x - self.min_x))
            return (a/sx + a/bx)/2

    def copy(self):
        b = Point(self.max_x, self.max_y, self.color, self.k)
        b.update_XY(self.min_x, self.min_y)
        return b


def split(img_path, h=50, w=50):
    img = Image.open(img_path)
    img = img.convert("RGB")
    array = np.asarray(img)
    shape = array.shape
    top12 = []
    # 遍历RGB三通道
    for k in range(array.shape[2]):
        hash = []
        for i in range(256):
            p = Point(0, 0, i, k)
            hash.append(p)
        ns = array[:, :, k]
        for y in range(len(ns)):
            for x in range(len(ns[y])):
                color = ns[y][x]
                color = color if 0 < color < 256 else 0
                if hash[color] is not None:
                    hash[color].update_XY(x, y)
                else:
                    p = Point(x, y, color)
                    p.n = 1
                    hash[color] = p
        top12.extend(hash)
    top12.sort(key=lambda a: a.n, reverse=True)
    top12 = top12[:min(24, len(top12))]  # 保留24个

    for i in range(len(top12)):
        top12[i] = series_search(array, top12[i])

    top12.sort(key=lambda a: a.n, reverse=True)
    counts = 0

    # 根据像素个数进行过滤
    for i in range(len(top12)):
        if counts/(i+1) > 2*(top12[i].n):
            top12 = top12[:i]
            break
        counts += top12[i].n
    # 重排序，根据min_x

    top12.sort(key=lambda a: a.min_x, reverse=False)
    i = 12
    # while len(top12) >= 4 and i > 0:
    #     max_si = [-1, -1, 0]
    #     i -= 1  # 死循环控制
    #     # 计算一次相邻不同通道相似度
    #     for i in range(len(top12) - 1):
    #         if top12[i].k != top12[i + 1].k:
    #             si = [i, i + 1, top12[i].similar(top12[i + 1])]
    #             max_si = max_si if max_si[-1] > max_si[-1] else si
    #     if len(max_si) > 0 and max_si[0] >= 0:
    #         index = 0 if top12[i].n < top12[i+1].n else 1  # 保留n最大的
    #         top12.remove(top12[max_si[index]])
    #     else:
    #         break
    imgs = []  # 四个最终的像素矩阵,纯布尔矩阵

    ks = {}
    for p in top12:
        if ks.get(str(p.k)) is None:
            ks[str(p.k)] = 1
        else:
            ks[str(p.k)] += 1
    max_k = 0
    for key in ks.keys():
        if ks[str(key)] > ks[str(max_k)]:
            max_k = key
    ttttt = test_top12(top12, array)
    a = 1

    for p in top12:
        if p.k != int(max_k):
            continue
        sub_array = to_bool(array, p)
        sub_array = not_bool(sub_array)
        sub_array = add_arrays(sub_array, w=w, h=h, num=1)
        img = Image.fromarray(sub_array)
        imgs.append(img)
        i += 1
    return imgs


def series_search(array, op):
    array = to_bool(array, op)
    hash = {}
    t_ps = np.transpose(np.nonzero(array))
    add = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    p_max = Point(-1, -1)
    for y, x in t_ps:
        p = Point(x, y)
        ns = [[y, x]]
        key = key = 'i:{:}j{:}'.format(x, y)
        if hash.get(key) is not None:
            continue
        for y, x in ns:
            for x_add, y_add in add:
                y_new, x_new = y+y_add, x+x_add
                key = 'i:{:}j{:}'.format(x_new, y_new)
                if 0 <= y_new < len(array) and 0 <= x_new < len(array[0]) and array[y_new][x_new] == True and \
                        hash.get(key) is None:
                    ns.append([y_new, x_new])
                    hash[key] = 1
                    p.update_XY(x_new, y_new)
        p_max = p_max if p_max.n > p.n else p
    p_max.min_y = p_max.min_y + op.min_y
    p_max.max_y = p_max.max_y + op.min_y
    p_max.min_x = p_max.min_x + op.min_x
    p_max.max_x = p_max.max_x + op.min_x
    p_max.color = op.color
    p_max.k = op.k
    return p_max


def all_split():
    for i in range(1, 2000):
        j = str(i).zfill(4)
        img_path = '../img/code_{:}.png'.format(j)
        imgs = split(img_path, w=50, h=50)
        array = np.asarray(imgs[0])
        for k in range(1, len(imgs)):
            a = np.asarray(imgs[k])
            array = np.hstack((array, a))
        img = Image.fromarray(array)
        img.save('../code/code_{:}.png'.format(j))
        print(i)


def excel():
    ss = ''
    for i in range(0, 1200):
        j = str(i).zfill(4)
        s = '<table><img src="C:\code\soushu\code\code_{:}.png" width="100"height="40">'.format(j)
        ss += s
    print(ss)


def read_label_from_cvs(csv_file_path):
    reader = csv.reader(open(csv_file_path, encoding='utf-8'))
    i = 0
    labels = {}
    for r in reader:
        label = r[0].strip()
        i += 1
        if len(label) != 4:
            continue
        k = str(i).zfill(4)
        labels[k] = label
    return labels


def split_img_by_label(source_img_path, object_img_path, labels, tp=0.8):
    if not os.path.exists(os.path.join(object_img_path, 'train')):
        os.mkdir(os.path.join(object_img_path, 'train'))
    if not os.path.exists(os.path.join(object_img_path, 'predict')):
        os.mkdir(os.path.join(object_img_path, 'predict'))

    for fn in os.listdir(source_img_path):
        i = fn.replace('code_', '').replace('.png', '').strip()

        if i not in labels.keys():
            continue
        label = labels[i].strip()
        imgs = split(os.path.join(source_img_path, fn))
        for j in range(len(label)):
            if j >= len(imgs):
                continue
            s = label[j]
            img = imgs[j]
            r = random.Random()
            sub_dir = 'train' if r.randint(0, 100) <= 100 * tp else 'predict'
            if not os.path.exists(os.path.join(object_img_path, sub_dir, s)):
                os.mkdir(os.path.join(object_img_path, sub_dir, s))
            img.save(os.path.join(object_img_path, sub_dir, s, '{:}_{:}.png'.format(i, j+1)))
            print('save {:} {:}'.format(fn, j+1))


if __name__ == '__main__':
    # imgs = split('../img/code_0143.png')
    # for i in range(len(imgs)):
    #     img = imgs[i]
    #     img.save('code_{:}.png'.format(i))
    # all_split()
    # excel()
    labels = read_label_from_cvs(r'C:\Users\qwer1\Desktop\label.csv')
    print(labels)
    split_img_by_label('../img', '../sub', labels)