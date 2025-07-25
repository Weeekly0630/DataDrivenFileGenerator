import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from modules.node.file_node import FileNode, DirectoryNode, FilePathResolver, BaseNode, FildSystemMetaDataNode

class TestFileNode(unittest.TestCase):
    def test_file_node_creation(self):
        node = FileNode("test.txt", None)
        self.assertEqual(node.meta_data.name, "test.txt")
        self.assertIsInstance(node._parent, BaseNode)

    def test_abs_path_and_rel_path(self):
        root = DirectoryNode("root", None, [])
        subdir = root.cretate_directory("subdir")
        file1 = root.create_file("file1.txt")
        file2 = subdir.create_file("file2.txt")

        # abs_path
        self.assertEqual(file1.abs_path, "/file1.txt")
        self.assertEqual(file2.abs_path, "/subdir/file2.txt")
        self.assertEqual(subdir.abs_path, "/subdir")
        self.assertEqual(root.abs_path, "/")

        # rel_path: file to root
        self.assertEqual(file1.rel_path(root), "file1.txt")
        self.assertEqual(file2.rel_path(root), "subdir/file2.txt")
        self.assertEqual(subdir.rel_path(root), "subdir")
        self.assertEqual(root.rel_path(root), ".")
        # rel_path: file to subdir
        self.assertEqual(file1.rel_path(subdir), "../file1.txt")
        self.assertEqual(file2.rel_path(subdir), "file2.txt")
        # rel_path: file to file
        self.assertEqual(file1.rel_path(file2), "../file1.txt")
        self.assertEqual(file2.rel_path(file1), "subdir/file2.txt")
        # rel_path: subdir to file
        self.assertEqual(subdir.rel_path(file2), ".")  # corrected
        self.assertEqual(subdir.rel_path(file1), "subdir")
        # rel_path: file to self
        self.assertEqual(file1.rel_path(file1), "file1.txt")
        self.assertEqual(file2.rel_path(file2), "file2.txt")
        # rel_path: subdir to self
        self.assertEqual(subdir.rel_path(subdir), ".")
        self.assertEqual(root.rel_path(root), ".")

class TestDirectoryNode(unittest.TestCase):
    def setUp(self):
        self.dir_node = DirectoryNode("root", None, [])

    def test_append_child(self):
        file_node = FileNode("file1.txt", None)
        self.dir_node.append_child(file_node)
        self.assertIn(file_node, [child.mapping_obj for child in self.dir_node._parent.children])
        self.assertEqual(file_node._parent.parent, self.dir_node._parent)

    def test_append_child_type_error(self):
        with self.assertRaises(TypeError):
            self.dir_node.append_child("not_a_node")  # type: ignore

    def test_append_child_value_error(self):
        file_node = FileNode("file2.txt", None)
        self.dir_node.append_child(file_node)
        with self.assertRaises(ValueError):
            self.dir_node.append_child(file_node)  # already has parent

    def test_create_file(self):
        file_node = self.dir_node.create_file("file3.txt")
        self.assertEqual(file_node.meta_data.name, "file3.txt")
        self.assertIn(file_node, [child.mapping_obj for child in self.dir_node._parent.children])

    def test_cretate_directory(self):
        sub_dir = self.dir_node.cretate_directory("subdir")
        self.assertEqual(sub_dir.meta_data.name, "subdir")
        self.assertIn(sub_dir, [child.mapping_obj for child in self.dir_node._parent.children])

    def test_normalize_path(self):
        path = FilePathResolver.normalize_path("./Test//Path\\to\\file/")
        self.assertEqual(path, "test/path/to/file")

    def test_build_tree(self):
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            # 创建子目录和文件
            os.mkdir(os.path.join(temp_dir, "subdir"))
            with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
                f.write("test")
            with open(os.path.join(temp_dir, "subdir", "file2.txt"), "w") as f:
                f.write("test2")

            dir_node = DirectoryNode("root", None, [])
            dir_node.build_tree(temp_dir, patterns="*.txt")
            # 检查根目录名归一化
            self.assertEqual(dir_node.meta_data.name, FilePathResolver.normalize_path(temp_dir))
            # 检查文件节点
            file_names = [child.mapping_obj.meta_data.name for child in dir_node._parent.children if isinstance(child.mapping_obj, FileNode)]
            self.assertIn("file1.txt", file_names)
            # 检查子目录节点
            dir_names = [child.mapping_obj.meta_data.name for child in dir_node._parent.children if isinstance(child.mapping_obj, DirectoryNode)]
            self.assertIn("subdir", dir_names)
        finally:
            shutil.rmtree(temp_dir)

class TestFindFunction(unittest.TestCase):
    def setUp(self):
        self.root = DirectoryNode("root", None, [])
        self.subdir = self.root.cretate_directory("subdir")
        self.file1 = self.root.create_file("file1.txt")
        self.file2 = self.subdir.create_file("file2.txt")
        self.file3 = self.subdir.create_file("file3.log")

    def test_find_by_name(self):
        result = self.root.find("file1.txt")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], FileNode)
        self.assertEqual(result[0].meta_data.name, "file1.txt")

        result = self.root.find("subdir")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], DirectoryNode)
        self.assertEqual(result[0].meta_data.name, "subdir")

    def test_find_by_wildcard(self):
        result = self.root.find("*.txt")
        names = [node.meta_data.name for node in result if isinstance(node, FileNode)]
        self.assertEqual(names, ["file1.txt"])

        result = self.root.find("subdir/*.txt")
        names = [node.meta_data.name for node in result if isinstance(node, FileNode)]
        self.assertEqual(sorted(names), ["file2.txt"])

    def test_find_by_double_star(self):
        result = self.root.find("**")
        names = [node.meta_data.name for node in result]
        self.assertIn("file1.txt", names)
        self.assertIn("file2.txt", names)
        self.assertIn("file3.log", names)
        self.assertIn("subdir", names)

        result = self.root.find("**/*.txt")
        names = [node.meta_data.name for node in result if isinstance(node, FileNode)]
        self.assertIn("file1.txt", names)
        self.assertIn("file2.txt", names)
        self.assertNotIn("file3.log", names)

    def test_find_absolute_path(self):
        abs_path = self.subdir.abs_path.lstrip("/")
        result = self.root.find(f"/{abs_path}/file2.txt")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].meta_data.name, "file2.txt")

    def test_find_not_found(self):
        result = self.root.find("not_exist.txt")
        self.assertEqual(result, [])

    def test_find_dot_and_dotdot(self):
        result = self.subdir.find(".")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], DirectoryNode)
        self.assertEqual(result[0].meta_data.name, "subdir")

        result = self.subdir.find("..")
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], DirectoryNode)
        self.assertEqual(result[0].meta_data.name, "root")

if __name__ == "__main__":
    unittest.main()
