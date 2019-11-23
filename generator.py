from abc import ABC, abstractmethod
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

    def is_valid_point(self, x, y):
        return 0 <= x <= 1 and 0 <= y <= 1

    def generate_point(self, i, prev_point):
        pass


class UniformGenerator(PointGenerator):

    def __init__(self, card, geo, dim, dist, output, output_format):
        super(UniformGenerator, self).__init__(card, geo, dim, dist, output, output_format)

    def generate_point(self, i, prev_point):
        x = random()
        y = random()
        return [x, y]


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
                      help='The available distributions are: {uniform, diagonal, gaussian, sierpinsky, bit, parcel}')
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
        pass
    elif dist == 'gaussian':
        pass
    elif dist == 'sierpinsky':
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
