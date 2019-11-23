from optparse import OptionParser


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
        card, geo, dim, dist, output, format = options_dict['card'], options_dict['geo'], options_dict['dim'], \
                                               options_dict['dist'], options_dict['output'], options_dict['format']
        print('{0}, {1}, {2}, {3}, {4}, {5}'.format(card, geo, dim, dist, output, format))
    except RuntimeError:
        print('Please check your arguments')


if __name__ == "__main__":
    main()
