import os
import zipfile
import shutil
import glob
from xml.dom import minidom

def unzip_docx(docx_path, output_dir):
    """解压 docx 文件到指定目录"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"解压完成: {docx_path} -> {output_dir}")

def zip_to_docx(input_dir, output_docx_path):
    """将目录内容压缩为 docx 文件"""
    with zipfile.ZipFile(output_docx_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, input_dir)
                zipf.write(abs_path, rel_path)
    print(f"压缩完成: {input_dir} -> {output_docx_path}")

def pretty_print_xml_file(xml_path, out_path=None):
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_str = f.read()
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
    if out_path:
        with open(out_path, 'wb') as f:
            f.write(pretty_xml)
    else:
        with open(xml_path, 'wb') as f:
            f.write(pretty_xml)

def pretty_print_xml_folder(folder_path):
    xml_files = glob.glob(os.path.join(folder_path, '**', '*.xml'), recursive=True)
    for xml_file in xml_files:
        pretty_print_xml_file(xml_file)

def compact_xml_file(xml_path):
    with open(xml_path, 'r', encoding='utf-8') as f:
        xml_str = f.read()
    dom = minidom.parseString(xml_str)
    compact_xml = dom.toxml(encoding='utf-8')
    with open(xml_path, 'wb') as f:
        f.write(compact_xml)

def compact_xml_folder(folder_path):
    xml_files = glob.glob(os.path.join(folder_path, '**', '*.xml'), recursive=True)
    for xml_file in xml_files:
        compact_xml_file(xml_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="docx文件解压/压缩工具，自动美化/恢复xml。参数自动推断：输入docx为解压，输入文件夹为压缩")
    parser.add_argument('input', type=str, nargs='?', help='docx文件或文件夹路径')
    parser.add_argument('output', type=str, nargs='?', help='输出目录或docx文件路径')
    args = parser.parse_args()

    def is_docx(path):
        return os.path.isfile(path) and path.lower().endswith('.docx')
    def is_folder(path):
        return os.path.isdir(path)

    if args.input and is_docx(args.input):
        outdir = args.output if args.output else os.path.splitext(args.input)[0] + '_unzip'
        unzip_docx(args.input, outdir)
        pretty_print_xml_folder(outdir)
        print("所有xml已美化，可直接用于Jinja开发。")
    elif args.input and is_folder(args.input):
        outdocx = args.output if args.output else args.input.rstrip('/\\') + '.docx'
        compact_xml_folder(args.input)
        zip_to_docx(args.input, outdocx)
        print("所有xml已恢复为紧凑格式并压缩为docx。")
    else:
        print("参数错误: 第一个参数应为docx文件或文件夹路径")
        print("\n用法示例:")
        print("解压并美化:  python convert.py input.docx [output_folder]")
        print("压缩并恢复:  python convert.py input_folder [output.docx]")
        print("\nWindows PowerShell/CMD 可直接运行以上命令。")
