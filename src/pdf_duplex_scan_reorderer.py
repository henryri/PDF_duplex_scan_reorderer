import math
from itertools import zip_longest
from typing import Iterator
import os
from pypdf import PdfReader, PdfWriter


def flat_zip(*iterators: Iterator, zip_function=zip):
    """
    Zips the items yielded by iterator, but instead of returning tuples,
    it returns the items in the tuples.

    e.g. list(flat_zip([1, 2],['a', 'b']) = [1, 'a', 2, 'b']
    :param iterators:  Iteratores
    :param zip_function: function used to zip the iterators (to allow zip_longest and similar)
    :return: items from within the iterators
    """
    for tup in zip_function(*iterators):
        for v in tup:
            yield v


def gen_page_order(page_cnt: int):
    """
    Creates an iterator that sorts the pages in the new order
    :param page_cnt: Overall page count of the document, if even assumes last page was empty and not included
    :return: iterator of page numbers belonging to the old document (starting with 0),
        yields in order they should be in the new document
    """
    # use int() to convert float, since we need int any way
    last_front_page = int(math.ceil(page_cnt / 2))
    front_pages = range(0, last_front_page)
    back_pages = range(page_cnt - 1, last_front_page - 1, -1)
    # front_pages could have a different amount of elements in case of odd page number
    # so use zip_longest and ignore None
    pages_ordered = (x for x in flat_zip(front_pages, back_pages, zip_function=zip_longest) if x is not None)
    return pages_ordered


def reorder_pdf(input_filename: str):
    """
    Reorders pages in a PDF:
        it assumes you scanned front pages first and than the back pages in inverse order
        (as you would if you just flipped the stack of paper).

        In case of an odd page number, it assumes, the last page does not have a (scanned) back side
    :param input_filename: name of the pdf to reorder
    """
    temp_filename = input_filename + ".tmp"
    with open(input_filename, "rb") as readfile:
        input_pdf = PdfReader(readfile)
        page_cnt = len(input_pdf.pages)
        pages_ordered = gen_page_order(page_cnt)
        with open(temp_filename, "wb") as writefile:
            output_pdf = PdfWriter()
            for page_no in pages_ordered:
                output_pdf.add_page(input_pdf.pages[page_no])
            output_pdf.write(writefile)
    os.remove(input_filename)
    os.rename(temp_filename, input_filename)


def parse_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description="""
        Reorders pages in a PDF:
            it assumes you scanned front pages first and than the back pages in inverse order
            (as you would if you just flipped the stack of paper).

            In case of an odd page number, it assumes, the last page does not have a (scanned) back side""")
    parser.add_argument("input", help="Name of PDF to reorder")
    args = parser.parse_args(args)
    return args


def main():
    """ main function """
    args = parse_args()

    reorder_pdf(input_filename=args.input)


if __name__ == '__main__':
    main()