from abc import ABC, abstractmethod
import math
from optparse import OptionParser
import os
from random import random
import sys


class Generator(ABC):

    def __init__(self, card, geo, dim, dist, output, output_format):
        self.card = card
        self.geo = geo
        self.dim = dim
        self.dist = dist
        self.output = output
        self.output_format = output_format

    def bernoulli(self, p):
        return 1 if random() < p else 0

    def normal(self, mu, sigma):
        return mu + sigma * math.sqrt(-2 * math.log(random())) * math.sin(2 * math.pi * random())

    def is_valid_point(self, x, y):
        return 0 <= x <= 1 and 0 <= y <= 1

    @abstractmethod
    def generate_point(self, i, prev_point):
        pass


class PointGenerator(Generator):

    def __init__(self, card, geo, dim, dist, output, output_format):
        super(PointGenerator, self).__init__(card, geo, dim, dist, output, output_format)

    def generate(self):
        geometries = []
        prev_point = None

        i = 0
        while i < self.card:
            x, y = self.generate_point(i, prev_point)

            if self.is_valid_point(x, y):
                prev_point = [x, y]
                geometries.append(prev_point)
                i = i + 1

        return geometries

    def generate_point(self, i, prev_point):
        pass


class UniformGenerator(PointGenerator):

    def __init__(self, card, geo, dim, dist, output, output_format):
        super(UniformGenerator, self).__init__(card, geo, dim, dist, output, output_format)

    def generate_point(self, i, prev_point):
        x = random()
        y = random()
        return [x, y]


class DiagonalGenerator(PointGenerator):
    def __init__(self, card, geo, dim, dist, output, output_format, percentage, buffer):
        super(DiagonalGenerator, self).__init__(card, geo, dim, dist, output, output_format)
        self.percentage = percentage
        self.buffer = buffer

    def generate_point(self, i, prev_point):
        if self.bernoulli(self.percentage) == 1:
            x = y = random()
        else:
            c = random()
            d = self.normal(0, self.buffer/5)
            x = c + d / math.sqrt(2)
            y = c - d / math.sqrt(2)
        return [x, y]


class GaussianGenerator(PointGenerator):
    def __init__(self, card, geo, dim, dist, output, output_format):
        super(GaussianGenerator, self).__init__(card, geo, dim, dist, output, output_format)

    def generate_point(self, i, prev_point):
        x = self.normal(0.5, 0.1)
        y = self.normal(0.5, 0.1)
        return [x, y]


class SierpinskiGenerator(PointGenerator):
    pass


class BitGenerator(PointGenerator):
    pass


class ParcelGenerator(PointGenerator):
    pass


def main():
    """
    Generate a list of geometries and write the list to file
    :return:
    """

    parser = OptionParser()
    parser.add_option('-c', '--card', type='int', help='The number of records to generate')
    parser.add_option('-g', '--geo', type='string',
                      help='Geometry type. Currently the generator supports {point, rectangle}')
    parser.add_option('-d', '--dim', type='int',
                      help='The dimensionality of the generated geometries. Currently, on two-dimensional data is supported.')
    parser.add_option('-t', '--dist', type='string',
                      help='The available distributions are: {uniform, diagonal, gaussian, sierpinsk, bit, parcel}')
    parser.add_option('-p', '--percentage', type='float',
                      help='The percentage (ratio) of the points that are exactly on the line.')
    parser.add_option('-b', '--buffer', type='float',
                      help='The size of the buffer around the line where additional geometries are scattered')
    parser.add_option('-o', '--output', type='string', help='Path to the output file')
    parser.add_option('-f', '--format', type='string',
                      help='Output format. Currently the generator supports {csv, wkt}')

    (options, args) = parser.parse_args()
    options_dict = vars(options)
    print(options_dict)
    try:
        card, geo, dim, dist, output, output_format = options_dict['card'], options_dict['geo'], options_dict['dim'], \
                                               options_dict['dist'], options_dict['output'], options_dict['format']
        # print('{0}, {1}, {2}, {3}, {4}, {5}'.format(card, geo, dim, dist, output, output_format))
    except RuntimeError:
        print('Please check your arguments')

    if dist == 'uniform':
        generator = UniformGenerator(card, geo, dim, dist, output, output_format)
    elif dist == 'diagonal':
        percentage = options_dict['percentage']
        buffer = options_dict['buffer']
        generator = DiagonalGenerator(card, geo, dim, dist, output, output_format, percentage, buffer)
        pass
    elif dist == 'gaussian':
        generator = GaussianGenerator(card, geo, dim, dist, output, output_format)
    elif dist == 'sierpinski':
        pass
    elif dist == 'bit':
        pass
    elif dist == 'parcel':
        pass
    else:
        print('Please check the distribution type.')
        sys.exit()

    geometries = generator.generate()

    if not os.path.exists('output'):
        os.mkdir('output')

    output_filename = 'output/{0}.{1}'.format(output, output_format)
    f = open(output_filename, 'w', encoding='utf8')

    if output_format == 'csv':
        for g in geometries:
            f.writelines('{0}\n'.format(','.join(str(x) for x in g)))

    elif output_format == 'wkt':
        for g in geometries:
            f.writelines('POINT ({0})\n'.format(' '.join(str(x) for x in g)))
    else:
        print('Please check the output format.')
        sys.exit()

    f.close()


if __name__ == "__main__":
    main()
