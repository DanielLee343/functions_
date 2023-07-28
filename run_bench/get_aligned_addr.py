import sys

PAGE_SIZE = 4096


def align_2_page(not_aligned_addr):
    remainder = not_aligned_addr % PAGE_SIZE
    if remainder <= 2048:
        not_aligned_addr -= remainder
    else:
        not_aligned_addr += PAGE_SIZE - remainder
    print("aligned:", not_aligned_addr)


not_aligned = int(sys.argv[1])
align_2_page(not_aligned)
