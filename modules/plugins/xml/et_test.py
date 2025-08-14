import xml.etree.ElementTree as ET

# 示例 XML 字符串
data = '''
<root>
    <var name="Speed" value="100" type="int"/>
    <ctr name="Config">
        <var name="Enable" value="true" type="bool"/>
        <lst name="Items">
            <var name="Item1" value="A"/>
            <var name="Item2" value="B"/>
        </lst>
    </ctr>
    <chc name="Mode" default="auto">
        aa
        <var name="Manual"/>
        aa
        <var name="Auto"/>
        aa
    </chc>
    <ref name="Ref1" target="Speed"/>
</root>
'''

root = ET.fromstring(data)

# 打印根节点信息
print(f"Root tag: {root.tag}")
print(f"Children count: {len(root)}")

# 遍历一级子节点
for child in root:
    print(f"Child tag: {child.tag}, attrib: {child.attrib}, text: {child.text}")

# 递归打印所有节点
def print_et_tree(elem, depth=0):
    indent = '  ' * depth
    print(f"{indent}{elem.tag} {elem.attrib} text={repr(elem.text)} tail={repr(elem.tail)}")
    for child in elem:
        print_et_tree(child, depth+1)

print("\n--- Tree Structure ---")
print_et_tree(root)
