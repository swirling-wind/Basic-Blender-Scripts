import bpy
import json
import os

def get_default_values(node_type):
    """获取指定节点类型的默认参数值"""
    # 创建一个临时材质来获取默认值
    temp_mat = bpy.data.materials.new('__temp_material__')
    temp_mat.use_nodes = True
    
    # 清除默认节点
    while temp_mat.node_tree.nodes:
        temp_mat.node_tree.nodes.remove(temp_mat.node_tree.nodes[0])
    
    # 创建指定类型的节点
    temp_node = temp_mat.node_tree.nodes.new(node_type)
    
    # 收集默认值
    default_values = {}
    
    # 收集输入参数默认值
    for input in temp_node.inputs:
        if hasattr(input, 'default_value'):
            if hasattr(input.default_value, '__len__'):
                if len(input.default_value) <= 4:  # 处理颜色和向量
                    default_values[input.name] = list(input.default_value)
            else:
                default_values[input.name] = input.default_value
    
    # 收集节点属性默认值
    for prop in dir(temp_node):
        if not prop.startswith('__') and not callable(getattr(temp_node, prop)):
            try:
                value = getattr(temp_node, prop)
                if isinstance(value, (int, float, bool, str)):
                    default_values[prop] = value
            except:
                pass
    
    # 删除临时材质
    bpy.data.materials.remove(temp_mat)
    
    return default_values

def format_value(value):
    """格式化参数值，使其更易读"""
    if isinstance(value, (list, tuple)) and len(value) <= 4:
        # 处理颜色和向量
        return f"[{', '.join([f'{v:.3f}' if isinstance(v, float) else str(v) for v in value])}]"
    elif isinstance(value, float):
        return f"{value:.3f}"
    else:
        return str(value)

def get_image_texture_info(node):
    """获取图像纹理节点的特殊信息"""
    info = []
    
    # 获取图像信息
    if node.image:
        # 尝试获取文件名
        if node.image.filepath:
            # 从文件路径中提取实际文件名
            filename = os.path.basename(node.image.filepath)
            info.append(f"图像文件: {filename}")
        elif node.image.packed_file:
            # 对于打包的文件
            info.append(f"图像文件: {node.image.name} (已打包)")
        else:
            # 如果没有文件路径，使用图像名称
            info.append(f"图像名称: {node.image.name}")
            
        # 添加图像尺寸信息
        info.append(f"图像尺寸: {node.image.size[0]}x{node.image.size[1]}")
        
        # 显示Color Space
        if hasattr(node.image, 'colorspace_settings'):
            info.append(f"Color Space: {node.image.colorspace_settings.name}")
    else:
        # 如果没有图像数据
        info.append("图像: 未指定")
    
    # 添加插值方式
    if hasattr(node, 'interpolation'):
        info.append(f"插值方式: {node.interpolation}")
    
    # 添加投影方式
    if hasattr(node, 'projection'):
        info.append(f"投影方式: {node.projection}")
    
    return info

def generate_material_nodes_markdown():
    """生成当前选中物体的材质节点信息的Markdown"""
    obj = bpy.context.active_object
    
    if not obj:
        return "**错误**: 没有选中的物体"
    
    if not obj.material_slots:
        return f"**信息**: 物体 '{obj.name}' 没有材质"
    
    md_output = f"# '{obj.name}' 物体材质节点信息\n\n"
    
    for mat_slot in obj.material_slots:
        mat = mat_slot.material
        
        if not mat or not mat.use_nodes:
            md_output += f"## 材质 '{mat.name if mat else 'None'}' 没有使用节点\n\n"
            continue
        
        md_output += f"## 材质: {mat.name}\n\n"
        
        # 获取所有节点
        md_output += "### 节点信息\n\n"
        md_output += "| 节点ID | 节点名称 | 节点类型 | 参数值 |\n"
        md_output += "| ------ | -------- | -------- | ------ |\n"
        
        for i, node in enumerate(mat.node_tree.nodes):
            # 获取节点类型的默认值
            default_values = get_default_values(node.bl_idname)
            
            # 收集非默认参数值
            non_default_params = []
            
            # 处理特殊节点类型（图像纹理）
            if node.bl_idname == 'ShaderNodeTexImage':
                non_default_params.extend(get_image_texture_info(node))
            
            # 检查输入参数
            for input in node.inputs:
                if hasattr(input, 'default_value') and not input.is_linked:
                    param_name = input.name
                    param_value = input.default_value
                    
                    # 检查是否为非默认值
                    is_default = False
                    if param_name in default_values:
                        if hasattr(param_value, '__len__'):
                            if len(param_value) <= 4:
                                is_default = list(param_value) == default_values[param_name]
                        else:
                            is_default = param_value == default_values[param_name]
                    
                    if not is_default:
                        if hasattr(param_value, '__len__'):
                            if len(param_value) <= 4:  # 处理颜色和向量
                                non_default_params.append(f"{param_name}: {format_value(param_value)}")
                        else:
                            non_default_params.append(f"{param_name}: {format_value(param_value)}")
            
            # 检查节点属性，排除一些特定属性
            excluded_props = ['select', 'dimensions', 'height', 'width', 'location', 'parent', 'name', 'bl_idname', 'bl_label']
            
            for prop in dir(node):
                if (not prop.startswith('__') and 
                    not callable(getattr(node, prop)) and 
                    prop not in excluded_props):
                    try:
                        value = getattr(node, prop)
                        if isinstance(value, (int, float, bool, str)):
                            if prop in default_values and value != default_values[prop]:
                                non_default_params.append(f"{prop}: {format_value(value)}")
                            elif prop not in default_values:
                                non_default_params.append(f"{prop}: {format_value(value)}")
                    except:
                        pass
            
            params_text = "<br>".join(non_default_params) if non_default_params else "使用默认值"
            md_output += f"| {i} | {node.name} | {node.bl_idname} | {params_text} |\n"
        
        # 获取节点连接
        md_output += "\n### 节点连接\n\n"
        if mat.node_tree.links:
            for link in mat.node_tree.links:
                from_node = link.from_node.name
                from_socket = link.from_socket.name
                to_node = link.to_node.name
                to_socket = link.to_socket.name
                
                md_output += f"- `{from_node}` 的 `{from_socket}` → `{to_node}` 的 `{to_socket}`\n"
        else:
            md_output += "没有节点连接\n"
        
        md_output += "\n---\n\n"
    
    return md_output



os.system("cls")
markdown_output = generate_material_nodes_markdown()
print(markdown_output)
