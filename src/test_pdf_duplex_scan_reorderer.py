from os import unlink
from os.path import exists
from unittest import TestCase

from pypdf import PdfReader, PdfWriter

from pdf_duplex_scan_reorderer import flat_zip, gen_page_order, reorder_pdf, parse_args


class TestPdfDuplexScanReorderer(TestCase):
    def setUp(self):
        self.output_pdf_name = "test_ouput.pdf"
        self.three_page_pdf = "three_page_scan.pdf"

    def tearDown(self):
        if exists(self.output_pdf_name):
            unlink(self.output_pdf_name)
        if exists(self.three_page_pdf):
            unlink(self.three_page_pdf)

    def test_flat_zip(self):
        self.assertListEqual(list(flat_zip([1, 2], ['a', 'b'])),
                             [1, 'a', 2, 'b'])

    def test_gen_page_order(self):
        with self.subTest("Even page count"):
            self.assertListEqual(list(gen_page_order(4)), [0, 3, 1, 2])

        with self.subTest("Odd page count"):
            self.assertListEqual(list(gen_page_order(5)), [0, 4, 1, 3, 2])

    def test_real_pdf_reorder(self):
        self._create_three_page_pdf()

        reorder_pdf(input_filename=self.three_page_pdf, output_filename=self.output_pdf_name)
        with open(self.output_pdf_name, "rb") as output_file:
            reader = PdfReader(output_file)
            self.assertEqual(len(reader.pages), 3,
                             msg="Resulting PDF should have 3 pages, as did the input")

    def _create_three_page_pdf(self):
        writer = PdfWriter()
        for _ in range(3):
            writer.add_blank_page(200, 400)
        with open(self.three_page_pdf, "wb") as three_page_pdf_file:
            writer.write(three_page_pdf_file)

    def test_argparser(self):
        res = parse_args(args=["1", "2"])
        self.assertEqual(res.input, "1")
        self.assertEqual(res.output, "2")
