import os
import sys
import glob
from xml.dom import minidom


def pretty_print_xml_file(xml_path, out_path=None):
    """美化单个xml文件内容"""
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_str = f.read()
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
    if out_path:
        with open(out_path, 'wb') as f:
            f.write(pretty_xml)
        print(f"美化输出: {xml_path} -> {out_path}")
    else:
        print(pretty_xml.decode('utf-8'))


def pretty_print_xml_folder(folder_path, out_folder=None):
    """美化文件夹下所有xml文件"""
    xml_files = glob.glob(os.path.join(folder_path, '**', '*.xml'), recursive=True)
    for xml_file in xml_files:
        rel_path = os.path.relpath(xml_file, folder_path)
        out_path = None
        if out_folder:
            out_path = os.path.join(out_folder, rel_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
        pretty_print_xml_file(xml_file, out_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="美化xml文件内容")
    parser.add_argument('--file', type=str, help='单个xml文件路径')
    parser.add_argument('--out', type=str, help='美化输出文件路径')
    parser.add_argument('--folder', type=str, help='包含xml文件的文件夹路径')
    parser.add_argument('--outfolder', type=str, help='美化输出文件夹路径')
    args = parser.parse_args()

    if args.file:
        pretty_print_xml_file(args.file, args.out)
    elif args.folder:
        pretty_print_xml_folder(args.folder, args.outfolder)
    else:
        print("参数错误: 请指定 --file 或 --folder")
        print("\n用法示例:")
        print("美化单文件: python pretty_xml.py --file input.xml --out output.xml")
        print("美化文件夹: python pretty_xml.py --folder input_folder --outfolder output_folder")
