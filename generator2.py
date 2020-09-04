from abc import ABC, abstractmethod
import math
import queue
import random as rand
import sys
import time


class Generator(ABC):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format):
        self.card = card
        self.geo = geo
        self.dim = dim
        self.dist = dist
        self.sp = sp
        self.a = a
        self.output = output
        self.output_format = output_format

    def bernoulli(self, p):
        return 1 if rand.random() < p else 0

    def normal(self, mu, sigma):
        return mu + sigma * math.sqrt(-2 * math.log(rand.random())) * math.sin(2 * math.pi * rand.random())

    def is_valid_point(self, point):
        for x in point.coordinates:
            if not (0 <= x <= 1):
                return False
        return True

    @abstractmethod
    def generate(self):
        pass


class PointGenerator(Generator):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format):
        super(PointGenerator, self).__init__(card, geo, dim, dist, sp, a, output, output_format)

    def transform(self, point):
        x = point.coordinates[0]
        y = point.coordinates[1]
        x_prime = self.a[0] * x + self.a[1] * y + self.a[2]
        y_prime = self.a[3] * x + self.a[4] * y + self.a[5]
        point.coordinates[0] = x_prime
        point.coordinates[1] = y_prime
        return point

    def generate(self):
        geometries = []
        prev_point = None

        i = 0
        while i < self.card:
            point = self.generate_point(i, prev_point)

            if self.is_valid_point(point):
                prev_point = point
                prev_point = self.transform(prev_point)

                if self.geo == 'point':
                    geometries.append(prev_point)
                elif self.geo == 'rectangle':
                    box = Box(prev_point.coordinates[0], prev_point.coordinates[1], self.sp[0], self.sp[1])
                    geometries.append(box)

                i = i + 1

        return geometries

    def generate_and_write(self):

        output_filename = '{0}.{1}'.format(self.output, self.output_format)
        f = open(output_filename, 'w', encoding='utf8')

        prev_point = None

        i = 0
        while i < self.card:
            point = self.generate_point(i, prev_point)

            if self.is_valid_point(point):
                prev_point = point
                prev_point = self.transform(prev_point)

                if self.geo == 'point':
                    f.writelines('{0}\n'.format(prev_point.to_string(self.output_format)))
                elif self.geo == 'rectangle':
                    # width = rand.uniform(self.sp[0] / 2, self.sp[0])
                    # height = rand.uniform(self.sp[1] / 2, self.sp[1])
                    width = self.sp[0]
                    height = self.sp[1]
                    box = Box(prev_point.coordinates[0], prev_point.coordinates[1], width, height)
                    f.writelines('{0}\n'.format(box.to_string(self.output_format)))

                i = i + 1

        f.close()

    @abstractmethod
    def generate_point(self, i, prev_point):
        pass


class UniformGenerator(PointGenerator):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format):
        super(UniformGenerator, self).__init__(card, geo, dim, dist, sp, a, output, output_format)

    def generate_point(self, i, prev_point):
        coordinates = [rand.random() for d in range(self.dim)]
        return Point(coordinates)


class DiagonalGenerator(PointGenerator):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format, percentage, buffer):
        super(DiagonalGenerator, self).__init__(card, geo, dim, dist, sp, a, output, output_format)
        self.percentage = percentage
        self.buffer = buffer

    def generate_point(self, i, prev_point):
        if self.bernoulli(self.percentage) == 1:
            coordinates = [rand.random()] * self.dim
        else:
            c = rand.random()
            d = self.normal(0, self.buffer / 5)

            coordinates = [(c + (1 - 2 * (x % 2)) * d / math.sqrt(2)) for x in range(self.dim)]
        return Point(coordinates)


class GaussianGenerator(PointGenerator):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format):
        super(GaussianGenerator, self).__init__(card, geo, dim, dist, sp, a, output, output_format)

    def generate_point(self, i, prev_point):
        coordinates = [self.normal(0.5, 0.1) for d in range(self.dim)]
        return Point(coordinates)


class SierpinskiGenerator(PointGenerator):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format):
        super(SierpinskiGenerator, self).__init__(card, geo, dim, dist, sp, a, output, output_format)

    def generate_point(self, i, prev_point):
        if i == 0:
            return Point([0.0, 0.0])
        elif i == 1:
            return Point([1.0, 0.0])
        elif i == 2:
            return Point([0.5, math.sqrt(3) / 2])
        else:
            d = self.dice(5)

            if d == 1 or d == 2:
                return self.get_middle_point(prev_point, Point([0.0, 0.0]))
            elif d == 3 or d == 4:
                return self.get_middle_point(prev_point, Point([1.0, 0.0]))
            else:
                return self.get_middle_point(prev_point, Point([0.5, math.sqrt(3) / 2]))

    def dice(self, n):
        return math.floor(rand.random() * n) + 1

    def get_middle_point(self, point1, point2):
        middle_point_coords = []
        for i in range(len(point1.coordinates)):
            middle_point_coords.append((point1.coordinates[i] + point2.coordinates[i]) / 2)
        return Point(middle_point_coords)


class BitGenerator(PointGenerator):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format, prob, digits):
        super(BitGenerator, self).__init__(card, geo, dim, dist, sp, a, output, output_format)
        self.prob = prob
        self.digits = int(digits)

    def generate_point(self, i, prev_point):
        coordinates = [self.bit() for d in range(self.dim)]
        return Point(coordinates)

    def bit(self):
        num = 0.0
        for i in range(1, self.digits + 1):
            c = self.bernoulli(self.prob)
            num = num + c / (math.pow(2, i))
        return num


class ParcelGenerator(Generator):

    def __init__(self, card, geo, dim, dist, sp, a, output, output_format, split_range, dither):
        super(ParcelGenerator, self).__init__(card, geo, dim, dist, sp, a, output, output_format)
        self.split_range = split_range
        self.dither = dither

    def generate(self):
        geometries = []
        box = Box(0.0, 0.0, 1.0, 1.0)
        boxes = queue.Queue(self.card)
        boxes.put(box)

        while boxes.qsize() < self.card:
            # Dequeue the queue to get a box
            b = boxes.get()

            if b.w > b.h:
                # Split vertically if width is bigger than height
                split_size = b.w * rand.uniform(self.split_range, 1 - self.split_range)
                b1 = Box(b.x, b.y, split_size, b.h)
                b2 = Box(b.x + split_size, b.y, b.w - split_size, b.h)
            else:
                # Split horizontally if width is less than height
                split_size = b.h * rand.uniform(self.split_range, 1 - self.split_range)
                b1 = Box(b.x, b.y, b.w, split_size)
                b2 = Box(b.x, b.y + split_size, b.w, b.h - split_size)

            boxes.put(b1)
            boxes.put(b2)

        while not boxes.empty():
            b = boxes.get()
            b.w = b.w * (1.0 - rand.uniform(0.0, self.dither))
            b.h = b.h * (1.0 - rand.uniform(0.0, self.dither))
            geometries.append(b)

        return geometries


class Geometry(ABC):

    def to_string(self, output_format):
        if output_format == 'csv':
            return self.to_csv_string()
        elif output_format == 'wkt':
            return self.to_wkt_string()
        else:
            print('Please check the output format.')
            sys.exit()

    @abstractmethod
    def to_csv_string(self):
        pass

    @abstractmethod
    def to_wkt_string(self):
        pass


class Point(Geometry):

    def __init__(self, coordinates):
        self.coordinates = coordinates

    def to_csv_string(self):
        return ','.join(str(x) for x in self.coordinates)

    def to_wkt_string(self):
        return 'POINT ({0})'.format(' '.join(str(x) for x in self.coordinates))


class Box(Geometry):

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def to_csv_string(self):
        return '{},{},{},{}'.format(self.x, self.y, self.x + self.w, self.y + self.h)

    def to_wkt_string(self):
        x1, y1, x2, y2 = self.x, self.y, self.x + self.w, self.y + self.h
        return 'POLYGON (({} {}, {} {}, {} {}, {} {}, {} {}))'.format(x1, y1, x2, y1, x2, y2, x1, y2, x1, y1)


def generate(filename, dist, card, d, sp1, sp2, sp3, sp4, a1, a2, a3, a4, a5, a6):
    print('Generating dataset {}'.format(filename))
    start_time = time.time()

    sp = []
    sp.append(sp1)
    sp.append(sp2)
    sp.append(sp3)
    sp.append(sp4)

    a = []
    a.append(a1)
    a.append(a2)
    a.append(a3)
    a.append(a4)
    a.append(a5)
    a.append(a6)

    geo = 'rectangle'
    output = '{}'.format(filename)
    output_format = 'csv'
    if dist == 'uniform':
        generator = UniformGenerator(card, geo, d, dist, sp, a, output, output_format)

    elif dist == 'diagonal':
        percentage, buffer = sp3, sp4
        generator = DiagonalGenerator(card, geo, d, dist, sp, a, output, output_format, percentage, buffer)

    elif dist == 'gaussian':
        generator = GaussianGenerator(card, geo, d, dist, sp, a, output, output_format)

    elif dist == 'parcel':
        split_range, dither = sp3, sp4
        generator = ParcelGenerator(card, geo, d, dist, sp, a, output, output_format, split_range, dither)
    elif dist == 'bit':
        prob, digits = sp3, sp4
        generator = BitGenerator(card, geo, d, dist, sp, a, output, output_format, prob, digits)
    elif dist == 'sierpinski':
        generator = SierpinskiGenerator(card, geo, d, dist, sp, a, output, output_format)

    if dist != 'parcel':
        generator.generate_and_write()
    else:
        geometries = generator.generate()
        output = '{}.csv'.format(filename)
        f = open(output, 'w', encoding='utf8')
        for g in geometries:
            f.writelines('{0}\n'.format(g.to_string(output_format)))
        f.close()

    elapsed_time = time.time() - start_time
    print('Generated {} dataset in {} seconds'.format(filename, elapsed_time))


def main():
    print('Spatial data generator')

    filename = sys.argv[1]
    dist = sys.argv[2]
    card, d = int(sys.argv[3]), int(sys.argv[4])
    sp1, sp2, sp3, sp4 = float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8])
    a1, a2, a3, a4, a5, a6 = float(sys.argv[9]), float(sys.argv[10]), float(sys.argv[11]), float(sys.argv[12]), float(sys.argv[13]), float(sys.argv[14])

    generate(filename, dist, card, d, sp1, sp2, sp3, sp4, a1, a2, a3, a4, a5, a6)


if __name__ == "__main__":
    main()
