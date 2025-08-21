import os
import zipfile
import shutil

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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="docx文件解压/压缩工具")
    parser.add_argument('--unzip', type=str, help='要解压的docx文件路径')
    parser.add_argument('--outdir', type=str, help='解压输出目录')
    parser.add_argument('--zip', type=str, help='要压缩的文件夹路径')
    parser.add_argument('--outdocx', type=str, help='压缩输出docx文件路径')
    args = parser.parse_args()

    if args.unzip and args.outdir:
        unzip_docx(args.unzip, args.outdir)
    elif args.zip and args.outdocx:
        zip_to_docx(args.zip, args.outdocx)
    else:
        print("参数错误: 请指定解压或压缩操作")
