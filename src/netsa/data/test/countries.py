# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

import unittest

from netsa.data.countries import *

class CountryTest(unittest.TestCase):

    def test_area_num_1(self):
        self.assertEqual(get_area_numeric('IS'), 352)

    def test_area_num_2(self):
        self.assertEqual(get_area_numeric('gB'), 826)

    def test_area_num_3(self):
        self.assertEqual(get_area_numeric('SrB'), 688)

    def test_area_num_4(self):
        self.assertEqual(get_area_numeric('706'), 706)

    def test_area_num_5(self):
        self.assertEqual(get_area_numeric(428), 428)

    def test_area_num_6(self):
        self.assertEqual(get_area_numeric('uk'), 826)

    def test_area_num_9(self):
        self.assertEqual(get_area_numeric(34), 34)

    def test_area_num_10(self):
        self.assertEqual(get_area_numeric('142'), 142)

    def test_area_num_11(self):
        self.assertRaises(KeyError, get_area_numeric, 'aa')

    def test_area_num_12(self):
        self.assertRaises(KeyError, get_area_numeric, 'aaa')

    def test_area_num_13(self):
        self.assertRaises(KeyError, get_area_numeric, ' us ')

    def test_area_num_14(self):
        self.assertRaises(KeyError, get_area_numeric, '000')

    def test_area_num_15(self):
        self.assertRaises(KeyError, get_area_numeric, 0)

    def test_area_name_1(self):
        self.assertEqual(get_area_name('IS'), 'Iceland')

    def test_area_name_2(self):
        self.assertEqual(
            get_area_name('gB'),
            'United Kingdom of Great Britain and Northern Ireland')

    def test_area_name_3(self):
        self.assertEqual(get_area_name('SrB'), 'Serbia')

    def test_area_name_4(self):
        self.assertEqual(get_area_name('706'), 'Somalia')

    def test_area_name_5(self):
        self.assertEqual(get_area_name(428), 'Latvia')

    def test_area_name_6(self):
        self.assertEqual(
            get_area_name('uk'),
            'United Kingdom of Great Britain and Northern Ireland')

    def test_area_name_8(self):
        self.assertEqual(get_area_name('yu'), 'Yugoslavia')

    def test_area_name_9(self):
        self.assertEqual(get_area_name(34), 'Southern Asia')

    def test_area_name_10(self):
        self.assertEqual(get_area_name('142'), 'Asia')

    def test_area_name_11(self):
        self.assertRaises(KeyError, get_area_name, 'aa')

    def test_area_name_12(self):
        self.assertRaises(KeyError, get_area_name, 'aaa')

    def test_area_name_13(self):
        self.assertRaises(KeyError, get_area_name, ' us ')

    def test_area_name_14(self):
        self.assertRaises(KeyError, get_area_name, '000')

    def test_area_name_15(self):
        self.assertRaises(KeyError, get_area_name, 0)

    def test_area_tlds_1(self):
        self.assertEqual(get_area_tlds('IS'), ['is'])

    def test_area_tlds_2(self):
        self.assertEqual(sorted(get_area_tlds('gB')), ['gb', 'uk'])

    def test_area_tlds_3(self):
        self.assertEqual(get_area_tlds('SrB'), ['rs'])

    def test_area_tlds_4(self):
        self.assertEqual(get_area_tlds('706'), ['so'])

    def test_area_tlds_5(self):
        self.assertEqual(get_area_tlds(428), ['lv'])

    def test_area_tlds_6(self):
        self.assertEqual(sorted(get_area_tlds('uk')), ['gb', 'uk'])

    def test_area_tlds_8(self):
        self.assertEqual(get_area_tlds('yu'), [])

    def test_area_tlds_9(self):
        self.assertEqual(
            sorted(get_area_tlds(34)),
            ['af', 'bd', 'bt', 'in', 'ir', 'lk', 'mv', 'np', 'pk'])

    def test_area_tlds_10(self):
        self.assertEqual(
            sorted(get_area_tlds('142')),
            ['ae', 'af', 'am', 'az', 'bd', 'bh', 'bn', 'bt', 'cn', 'cy', 'ge',
             'hk', 'id', 'il', 'in', 'iq', 'ir', 'jo', 'jp', 'kg', 'kh', 'kp',
             'kr', 'kw', 'kz', 'la', 'lb', 'lk', 'mm', 'mn', 'mo', 'mv', 'my',
             'np', 'om', 'ph', 'pk', 'ps', 'qa', 'sa', 'sg', 'sy', 'th', 'tj',
             'tl', 'tm', 'tr', 'tw', 'uz', 'vn', 'ye'])

    def test_area_tlds_11(self):
        self.assertRaises(KeyError, get_area_tlds, 'aa')

    def test_area_tlds_12(self):
        self.assertRaises(KeyError, get_area_tlds, 'aaa')

    def test_area_tlds_13(self):
        self.assertRaises(KeyError, get_area_tlds, ' us ')

    def test_area_tlds_14(self):
        self.assertRaises(KeyError, get_area_tlds, '000')

    def test_area_tlds_15(self):
        self.assertRaises(KeyError, get_area_tlds, 0)

    def test_country_num_1(self):
        self.assertEqual(get_country_numeric('IS'), 352)

    def test_country_num_2(self):
        self.assertEqual(get_country_numeric('gB'), 826)

    def test_country_num_3(self):
        self.assertEqual(get_country_numeric('SrB'), 688)

    def test_country_num_4(self):
        self.assertEqual(get_country_numeric('706'), 706)

    def test_country_num_5(self):
        self.assertEqual(get_country_numeric(428), 428)

    def test_country_num_6(self):
        self.assertEqual(get_country_numeric('uk'), 826)

    def test_country_num_9(self):
        self.assertRaises(KeyError, get_country_numeric, 34)

    def test_country_num_10(self):
        self.assertRaises(KeyError, get_country_numeric, '142')

    def test_country_num_11(self):
        self.assertRaises(KeyError, get_country_numeric, 'aa')

    def test_country_num_12(self):
        self.assertRaises(KeyError, get_country_numeric, 'aaa')

    def test_country_num_13(self):
        self.assertRaises(KeyError, get_country_numeric, ' us ')

    def test_country_num_14(self):
        self.assertRaises(KeyError, get_country_numeric, '000')

    def test_country_num_15(self):
        self.assertRaises(KeyError, get_country_numeric, 0)

    def test_country_name_1(self):
        self.assertEqual(get_country_name('IS'), 'Iceland')

    def test_country_name_2(self):
        self.assertEqual(
            get_country_name('gB'),
            'United Kingdom of Great Britain and Northern Ireland')

    def test_country_name_3(self):
        self.assertEqual(get_country_name('SrB'), 'Serbia')

    def test_country_name_4(self):
        self.assertEqual(get_country_name('706'), 'Somalia')

    def test_country_name_5(self):
        self.assertEqual(get_country_name(428), 'Latvia')

    def test_country_name_6(self):
        self.assertEqual(
            get_country_name('uk'),
            'United Kingdom of Great Britain and Northern Ireland')

    def test_country_name_8(self):
        self.assertEqual(get_country_name('yu'), 'Yugoslavia')

    def test_country_name_9(self):
        self.assertRaises(KeyError, get_country_name, 34)

    def test_country_name_10(self):
        self.assertRaises(KeyError, get_country_name, '142')

    def test_country_name_11(self):
        self.assertRaises(KeyError, get_country_name, 'aa')

    def test_country_name_12(self):
        self.assertRaises(KeyError, get_country_name, 'aaa')

    def test_country_name_13(self):
        self.assertRaises(KeyError, get_country_name, ' us ')

    def test_country_name_14(self):
        self.assertRaises(KeyError, get_country_name, '000')

    def test_country_name_15(self):
        self.assertRaises(KeyError, get_country_name, 0)

    def test_country_alpha2_1(self):
        self.assertEqual(get_country_alpha2('IS'), 'IS')

    def test_country_alpha2_2(self):
        self.assertEqual(get_country_alpha2('gB'), 'GB')

    def test_country_alpha2_3(self):
        self.assertEqual(get_country_alpha2('SrB'), 'RS')

    def test_country_alpha2_4(self):
        self.assertEqual(get_country_alpha2('706'), 'SO')

    def test_country_alpha2_5(self):
        self.assertEqual(get_country_alpha2(428), 'LV')

    def test_country_alpha2_6(self):
        self.assertEqual(get_country_alpha2('uk'), 'GB')

    def test_country_alpha2_8(self):
        self.assertEqual(get_country_alpha2('yu'), 'YU')

    def test_country_alpha2_9(self):
        self.assertRaises(KeyError, get_country_alpha2, 34)

    def test_country_alpha2_10(self):
        self.assertRaises(KeyError, get_country_alpha2, '142')

    def test_country_alpha2_11(self):
        self.assertRaises(KeyError, get_country_alpha2, 'aa')

    def test_country_alpha2_12(self):
        self.assertRaises(KeyError, get_country_alpha2, 'aaa')

    def test_country_alpha2_13(self):
        self.assertRaises(KeyError, get_country_alpha2, ' us ')

    def test_country_alpha2_14(self):
        self.assertRaises(KeyError, get_country_alpha2, '000')

    def test_country_alpha2_15(self):
        self.assertRaises(KeyError, get_country_alpha2, 0)

    def test_country_alpha3_1(self):
        self.assertEqual(get_country_alpha3('IS'), 'ISL')

    def test_country_alpha3_2(self):
        self.assertEqual(get_country_alpha3('gB'), 'GBR')

    def test_country_alpha3_3(self):
        self.assertEqual(get_country_alpha3('SrB'), 'SRB')

    def test_country_alpha3_4(self):
        self.assertEqual(get_country_alpha3('706'), 'SOM')

    def test_country_alpha3_5(self):
        self.assertEqual(get_country_alpha3(428), 'LVA')

    def test_country_alpha3_6(self):
        self.assertEqual(get_country_alpha3('uk'), 'GBR')

    def test_country_alpha3_8(self):
        self.assertEqual(get_country_alpha3('yu'), 'YUG')

    def test_country_alpha3_9(self):
        self.assertRaises(KeyError, get_country_alpha3, 34)

    def test_country_alpha3_10(self):
        self.assertRaises(KeyError, get_country_alpha3, '142')

    def test_country_alpha3_11(self):
        self.assertRaises(KeyError, get_country_alpha3, 'aa')

    def test_country_alpha3_12(self):
        self.assertRaises(KeyError, get_country_alpha3, 'aaa')

    def test_country_alpha3_13(self):
        self.assertRaises(KeyError, get_country_alpha3, ' us ')

    def test_country_alpha3_14(self):
        self.assertRaises(KeyError, get_country_alpha3, '000')

    def test_country_alpha3_15(self):
        self.assertRaises(KeyError, get_country_alpha3, 0)

    def test_country_tlds_1(self):
        self.assertEqual(get_country_tlds('IS'), ['is'])

    def test_country_tlds_2(self):
        self.assertEqual(sorted(get_country_tlds('gB')), ['gb', 'uk'])

    def test_country_tlds_3(self):
        self.assertEqual(get_country_tlds('SrB'), ['rs'])

    def test_country_tlds_4(self):
        self.assertEqual(get_country_tlds('706'), ['so'])

    def test_country_tlds_5(self):
        self.assertEqual(get_country_tlds(428), ['lv'])

    def test_country_tlds_6(self):
        self.assertEqual(sorted(get_country_tlds('uk')), ['gb', 'uk'])

    def test_country_tlds_8(self):
        self.assertEqual(get_country_tlds('yu'), [])

    def test_country_tlds_9(self):
        self.assertRaises(KeyError, get_country_tlds, 34)

    def test_country_tlds_10(self):
        self.assertRaises(KeyError, get_country_tlds, '142')

    def test_country_tlds_11(self):
        self.assertRaises(KeyError, get_country_tlds, 'aa')

    def test_country_tlds_12(self):
        self.assertRaises(KeyError, get_country_tlds, 'aaa')

    def test_country_tlds_13(self):
        self.assertRaises(KeyError, get_country_tlds, ' us ')

    def test_country_tlds_14(self):
        self.assertRaises(KeyError, get_country_tlds, '000')

    def test_country_tlds_15(self):
        self.assertRaises(KeyError, get_country_tlds, 0)

    def test_iter_countries_1(self):
        self.assertEqual(len(list(iter_countries())), 276)

    def test_iter_countries_2(self):
        self.assertEqual(sorted(iter_countries())[0], 4)

    def test_iter_countries_3(self):
        self.assertEqual(sorted(iter_countries())[-1], 999)

    def test_region_numeric_1(self):
        self.assertEqual(get_region_numeric('030'), 30)

    def test_region_numeric_2(self):
        self.assertEqual(get_region_numeric(151), 151)

    def test_region_numeric_3(self):
        self.assertRaises(KeyError, get_region_numeric, 894)

    def test_region_name_1(self):
        self.assertEqual(get_region_name('030'), 'Eastern Asia')

    def test_region_name_2(self):
        self.assertEqual(get_region_name(151), 'Eastern Europe')

    def test_region_name_3(self):
        self.assertRaises(KeyError, get_region_name, 894)

    def test_region_tlds_1(self):
        self.assertEqual(
            sorted(get_region_tlds('030')),
            ['cn', 'hk', 'jp', 'kp', 'kr', 'mn', 'mo', 'tw'])

    def test_region_tlds_2(self):
        self.assertEqual(
            sorted(get_region_tlds(151)),
            ['bg', 'by', 'cz', 'hu', 'md', 'pl', 'ro', 'ru', 'sk', 'ua'])

    def test_region_tlds_3(self):
        self.assertRaises(KeyError, get_region_tlds, 894)

    def test_region_tlds_4(self):
        self.assertEqual(
            sorted(get_region_tlds(9)),
            ['as', 'au', 'ck', 'fj', 'fm', 'gu', 'ki', 'mh', 'mp', 'nc', 'nf',
             'nr', 'nu', 'nz', 'pf', 'pg', 'pn', 'pw', 'sb', 'tk', 'to', 'tv',
             'vu', 'wf', 'ws'])

    def test_iter_regions_1(self):
        self.assertEqual(sorted(iter_regions()),
                         [2, 9, 19, 142, 150, 990])

    def test_iter_region_subregions_1(self):
        self.assertEqual(sorted(iter_region_subregions(150)),
                         [39, 151, 154, 155])

    def test_iter_region_subregions_2(self):
        self.assertEqual(sorted(iter_region_subregions('009')),
                         [53, 54, 57, 61])

    def test_iter_region_subregions_3(self):
        self.assertEqual(sorted(iter_region_subregions(151)), [])

    def test_iter_region_subregions_4(self):
        self.assertRaises(KeyError, iter_region_subregions, 999)

    def test_iter_region_countries_1(self):
        self.assertEqual(sorted(iter_region_countries(39)),
                         [8, 20, 70, 191, 292, 300, 336, 380, 470, 499, 620,
                          674, 688, 705, 724, 807])

    def test_iter_region_countries_2(self):
        self.assertEqual(sorted(iter_region_countries('009')),
                         [16, 36, 90, 184, 242, 258, 296, 316, 520, 540, 548,
                          554, 570, 574, 580, 583, 584, 585, 598, 612, 772,
                          776, 798, 876, 882])

    def test_iter_region_countries_3(self):
        self.assertRaises(KeyError, iter_region_countries, 999)
