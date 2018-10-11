import argparse

from lex import LexScanner
from ast_parser import LRParser
from code_generate import CodeGenerator
from utils import get_filename, file_content_to_string

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="input file path")
    parser.add_argument("--save", default="./", help="save file path")
    args = parser.parse_args()
    source_file_path = args.path
    save_file_path = args.save
    print("source from the path => " + source_file_path)
    print("save file path => " + save_file_path)

    file = open(source_file_path)
    lines = file.readlines()
    file.close()
    file_content = file_content_to_string(lines)

    save_file_name = save_file_path + get_filename(source_file_path)

    print("Now Parsing...")
    scanner = LexScanner(file_content)
    parser = LRParser(scanner)
    parser.parse()
    parser.write_tree_to_file(save_file_name)
    print("Finish!")

    print("Now Generating code...")
    tree = parser.get_ast_tree()
    generator = CodeGenerator(tree)
    generator.generate()
    generator.write_code_to_file(save_file_name)
    print("Finish!")

if __name__ == "__main__":
    main()
