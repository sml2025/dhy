#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
马里奥乐高拼搭图生成器
生成高清拼搭图和详细材料清单
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime

class LegoMarioGenerator:
    def __init__(self):
        # 项目规格
        self.total_width_mm = 1000  # 1米
        self.total_height_mm = 1500  # 1.5米
        self.brick_size_mm = 15.8   # 每个乐高模块尺寸
        
        # 计算网格尺寸
        self.grid_width = int(self.total_width_mm / self.brick_size_mm)  # 63
        self.grid_height = int(self.total_height_mm / self.brick_size_mm)  # 95
        self.total_bricks = self.grid_width * self.grid_height  # 5,985
        
        # 乐高标准颜色
        self.lego_colors = {
            'white': '#F4F4F4',
            'black': '#1B2A34', 
            'red': '#C91A09',
            'blue': '#0055BF',
            'yellow': '#FFD700',
            'green': '#237841',
            'orange': '#FE8A18',
            'brown': '#582A12',
            'gray': '#9BA19D',
            'tan': '#E4CD9E',
            'darkblue': '#143044',
            'lightgray': '#BDC6AD'
        }
        
        # 中文颜色名称
        self.color_names_zh = {
            'white': '白色',
            'black': '黑色',
            'red': '红色',
            'blue': '蓝色',
            'yellow': '黄色',
            'green': '绿色',
            'orange': '橙色',
            'brown': '棕色',
            'gray': '灰色',
            'tan': '棕褐色',
            'darkblue': '深蓝色',
            'lightgray': '浅灰色'
        }
        
        # 马里奥像素图案（简化版）
        self.mario_pattern = self._create_mario_pattern()
        
    def _create_mario_pattern(self):
        """创建马里奥像素图案"""
        # 这是一个简化的马里奥图案
        pattern = []
        
        # 马里奥头部轮廓（简化）
        mario_design = [
            "000000rrrrr000000000000000000000000000000000000000000000000000",
            "0000rrrrrrrrrr0000000000000000000000000000000000000000000000000",
            "000rrrrrrrrrrrr000000000000000000000000000000000000000000000000",
            "00rrrbttttttbrr00000000000000000000000000000000000000000000000",
            "0rrbbtttttttbbr0000000000000000000000000000000000000000000000000",
            "0rbbtttttttttbr0000000000000000000000000000000000000000000000000",
            "rbbtttbbbbtttbr0000000000000000000000000000000000000000000000000",
            "rbttbbbbbbbbttbr000000000000000000000000000000000000000000000000",
            "rbtbbwwwwwwwbbtr000000000000000000000000000000000000000000000000",
            "rbtbwwbwwbwwbbtr000000000000000000000000000000000000000000000000",
            "rbtbwbbwwbbwbbtr000000000000000000000000000000000000000000000000",
            "rbtbwwbwwbwwbbtr000000000000000000000000000000000000000000000000",
            "rbtbbwwwwwwwbbtr000000000000000000000000000000000000000000000000",
            "rbtttbbbbbbbtttbr00000000000000000000000000000000000000000000000",
            "rbttttttttttttbr00000000000000000000000000000000000000000000000",
            "0rbttttttttttbr000000000000000000000000000000000000000000000000",
            "0rrbbtttttbbbrr000000000000000000000000000000000000000000000000",
            "00rrrbbbbbbrr0000000000000000000000000000000000000000000000000",
            "000rrrrrrrrrr0000000000000000000000000000000000000000000000000",
            "0000rrrrrrrr00000000000000000000000000000000000000000000000000",
            # 帽子上的M标志
            "000000rrrrr000000000000000000000000000000000000000000000000000",
            "00000rrrrrr000000000000000000000000000000000000000000000000000",
            "0000rrwwwrr000000000000000000000000000000000000000000000000000",
            "000rrwwmwwrr00000000000000000000000000000000000000000000000000",
            "00rrwwmmmwwrr0000000000000000000000000000000000000000000000000",
            "0rrwwmmmmmwwrr000000000000000000000000000000000000000000000000",
            "rrwwmmwwmmmwwrr00000000000000000000000000000000000000000000000",
            "rwwmmwwwwmmwwwr00000000000000000000000000000000000000000000000",
            "rwwmwwwwwwmwwwr00000000000000000000000000000000000000000000000",
            "rwwwwwwwwwwwwwr00000000000000000000000000000000000000000000000",
            "0rwwwwwwwwwwwr000000000000000000000000000000000000000000000000",
            "00rrwwwwwwwrr0000000000000000000000000000000000000000000000000",
            "000rrrrrrrr000000000000000000000000000000000000000000000000000",
        ]
        
        # 填充到网格大小
        while len(mario_design) < self.grid_height:
            mario_design.append("0" * self.grid_width)
            
        # 确保每行都是正确的长度
        for i, row in enumerate(mario_design):
            if len(row) < self.grid_width:
                mario_design[i] = row + "0" * (self.grid_width - len(row))
            elif len(row) > self.grid_width:
                mario_design[i] = row[:self.grid_width]
                
        return mario_design
    
    def generate_grid_data(self):
        """生成网格数据"""
        # 颜色映射
        color_map = {
            '0': 'white',     # 背景
            'r': 'red',       # 帽子
            'b': 'brown',     # 头发/胡子
            't': 'tan',       # 皮肤
            'w': 'white',     # 眼睛/牙齿
            'm': 'red',       # M标志
            'g': 'green',     # 可选绿色
            'y': 'yellow',    # 可选黄色
            'u': 'blue'       # 可选蓝色
        }
        
        grid_data = []
        for row in self.mario_pattern:
            grid_row = []
            for char in row:
                color = color_map.get(char, 'white')
                grid_row.append(color)
            grid_data.append(grid_row)
            
        return grid_data
    
    def calculate_materials(self, grid_data):
        """计算材料清单"""
        materials = {}
        
        for row in grid_data:
            for color in row:
                materials[color] = materials.get(color, 0) + 1
                
        return materials
    
    def generate_high_res_image(self, grid_data, output_path="mario_lego_blueprint.png"):
        """生成高清拼搭图"""
        # 每个格子在图片中的像素大小
        cell_pixel_size = 20
        
        # 计算图片尺寸
        img_width = self.grid_width * cell_pixel_size
        img_height = self.grid_height * cell_pixel_size
        
        # 创建图片
        img = Image.new('RGB', (img_width + 400, img_height + 200), 'white')
        draw = ImageDraw.Draw(img)
        
        # 绘制网格
        for y, row in enumerate(grid_data):
            for x, color in enumerate(row):
                # 获取颜色
                hex_color = self.lego_colors.get(color, '#FFFFFF')
                
                # 绘制格子
                x1 = x * cell_pixel_size
                y1 = y * cell_pixel_size
                x2 = x1 + cell_pixel_size
                y2 = y1 + cell_pixel_size
                
                draw.rectangle([x1, y1, x2, y2], fill=hex_color, outline='#CCCCCC')
                
                # 绘制格子编号（每10个格子显示一次）
                if x % 10 == 0 and y % 10 == 0:
                    text = f"{y+1}-{x+1}"
                    draw.text((x1 + 2, y1 + 2), text, fill='black')
        
        # 添加标题和信息
        try:
            # 尝试使用系统字体
            title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
            info_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 16)
        except:
            # 如果没有中文字体，使用默认字体
            title_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
        
        # 绘制标题
        draw.text((img_width + 20, 20), "马里奥乐高拼搭图", fill='black', font=title_font)
        
        # 绘制项目信息
        info_text = [
            f"总体尺寸: {self.total_width_mm}×{self.total_height_mm}mm",
            f"乐高模块尺寸: {self.brick_size_mm}×{self.brick_size_mm}mm", 
            f"网格数量: {self.grid_width}×{self.grid_height}格",
            f"总乐高数量: {self.total_bricks}块",
            "",
            "坐标说明:",
            "格子编号格式: 行号-列号",
            "例如: 1-1表示第1行第1列",
            "",
            "拼搭建议:",
            "1. 从底部向上逐行拼搭",
            "2. 相同颜色区域可批量处理",
            "3. 先完成轮廓再填充内部"
        ]
        
        y_offset = 60
        for line in info_text:
            draw.text((img_width + 20, y_offset), line, fill='black', font=info_font)
            y_offset += 25
        
        # 保存图片
        img.save(output_path, 'PNG', quality=95)
        print(f"高清拼搭图已保存: {output_path}")
        
        return output_path
    
    def generate_materials_report(self, materials, output_path="mario_materials_list.txt"):
        """生成详细材料清单报告"""
        report = []
        report.append("=" * 60)
        report.append("马里奥乐高拼搭项目 - 材料清单报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        report.append("")
        
        # 项目规格
        report.append("📐 项目规格:")
        report.append(f"  总体尺寸: {self.total_width_mm}mm × {self.total_height_mm}mm")
        report.append(f"  乐高模块尺寸: {self.brick_size_mm}mm × {self.brick_size_mm}mm")
        report.append(f"  网格数量: {self.grid_width}列 × {self.grid_height}行")
        report.append(f"  总乐高数量: {self.total_bricks:,}块")
        report.append("")
        
        # 材料清单
        report.append("🧱 材料清单:")
        report.append("-" * 40)
        
        total_used = 0
        materials_list = []
        
        for color, count in sorted(materials.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                color_name = self.color_names_zh.get(color, color)
                percentage = (count / self.total_bricks) * 100
                materials_list.append((color_name, count, percentage))
                total_used += count
                
        # 按数量排序显示
        for color_name, count, percentage in materials_list:
            report.append(f"  {color_name:10} : {count:6,}块 ({percentage:5.1f}%)")
            
        report.append("-" * 40)
        report.append(f"  总计使用    : {total_used:6,}块")
        report.append(f"  空白格子    : {self.total_bricks - total_used:6,}块")
        report.append("")
        
        # 成本估算
        report.append("💰 成本估算:")
        base_price = 0.5  # 每块乐高基础价格
        color_multipliers = {
            'white': 1.0,
            'black': 1.0,
            'red': 1.0,
            'blue': 1.0,
            'yellow': 1.0,
            'green': 1.0,
            'brown': 1.2,
            'orange': 1.1,
            'gray': 1.0,
            'tan': 1.3,
            'darkblue': 1.1,
            'lightgray': 1.0
        }
        
        total_cost = 0
        for color, count in materials.items():
            if count > 0 and color != 'white':  # 不计算白色底色成本
                multiplier = color_multipliers.get(color, 1.0)
                cost = count * base_price * multiplier
                total_cost += cost
                color_name = self.color_names_zh.get(color, color)
                report.append(f"  {color_name:10} : ¥{cost:8.2f} ({count}块 × ¥{base_price * multiplier:.2f})")
                
        report.append("-" * 40)
        report.append(f"  预估总成本  : ¥{total_cost:8.2f}")
        report.append("")
        
        # 购买建议
        report.append("🛒 购买建议:")
        report.append("  1. 建议按颜色分批购买，避免混乱")
        report.append("  2. 可考虑购买散装乐高降低成本")
        report.append("  3. 预留10%的余量应对损耗")
        report.append("  4. 优先购买用量大的颜色")
        report.append("")
        
        # 拼搭建议
        report.append("🔧 拼搭建议:")
        report.append("  1. 准备充足的工作空间")
        report.append("  2. 按颜色将乐高分类存放")
        report.append("  3. 从底部开始向上拼搭")
        report.append("  4. 每完成一行检查一次")
        report.append("  5. 拍照记录进度，便于对照")
        report.append("")
        
        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
            
        print(f"材料清单报告已保存: {output_path}")
        return output_path
    
    def generate_building_instructions(self, grid_data, output_path="mario_building_guide.txt"):
        """生成详细拼搭指南"""
        instructions = []
        instructions.append("=" * 60)
        instructions.append("马里奥乐高拼搭指南")
        instructions.append("=" * 60)
        instructions.append("")
        
        # 准备工作
        instructions.append("🔧 准备工作:")
        instructions.append("1. 准备一个平整的拼搭表面")
        instructions.append("2. 确保充足的照明")
        instructions.append("3. 按颜色将乐高积木分类")
        instructions.append("4. 准备本拼搭指南和材料清单")
        instructions.append("")
        
        # 拼搭步骤
        instructions.append("📋 拼搭步骤:")
        instructions.append("按行从下到上（第95行到第1行）依次拼搭")
        instructions.append("")
        
        # 逐行指南
        for y in range(len(grid_data) - 1, -1, -1):  # 从底部开始
            row = grid_data[y]
            row_num = y + 1
            
            instructions.append(f"第{row_num:2d}行:")
            
            # 统计这一行的颜色
            row_colors = {}
            for color in row:
                row_colors[color] = row_colors.get(color, 0) + 1
                
            # 显示这一行需要的材料
            materials_needed = []
            for color, count in row_colors.items():
                if color != 'white':
                    color_name = self.color_names_zh.get(color, color)
                    materials_needed.append(f"{color_name}{count}块")
                    
            if materials_needed:
                instructions.append(f"  需要: {', '.join(materials_needed)}")
            else:
                instructions.append("  需要: 全部为白色底色")
                
            # 详细位置指南
            instruction_line = "  "
            for x, color in enumerate(row):
                if color != 'white':
                    color_abbr = self.color_names_zh.get(color, color)[0]
                    instruction_line += f"{x+1:2d}({color_abbr}) "
                else:
                    instruction_line += f"{x+1:2d}(白) "
                    
                # 每20个格子换行
                if (x + 1) % 20 == 0:
                    instructions.append(instruction_line)
                    instruction_line = "  "
                    
            if instruction_line.strip():
                instructions.append(instruction_line)
                
            instructions.append("")
            
        # 保存指南
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(instructions))
            
        print(f"拼搭指南已保存: {output_path}")
        return output_path
    
    def generate_json_data(self, grid_data, materials, output_path="mario_lego_data.json"):
        """生成JSON格式的数据"""
        data = {
            "project_info": {
                "name": "马里奥乐高拼搭项目",
                "total_size_mm": [self.total_width_mm, self.total_height_mm],
                "brick_size_mm": self.brick_size_mm,
                "grid_size": [self.grid_width, self.grid_height],
                "total_bricks": self.total_bricks,
                "generated_time": datetime.now().isoformat()
            },
            "grid_data": grid_data,
            "materials": materials,
            "color_palette": self.lego_colors,
            "color_names": self.color_names_zh
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"JSON数据已保存: {output_path}")
        return output_path
    
    def run_complete_generation(self):
        """运行完整的生成流程"""
        print("开始生成马里奥乐高拼搭项目...")
        print(f"项目规格: {self.grid_width}×{self.grid_height} = {self.total_bricks:,}块")
        print()
        
        # 生成网格数据
        print("1. 生成网格数据...")
        grid_data = self.generate_grid_data()
        
        # 计算材料
        print("2. 计算材料清单...")
        materials = self.calculate_materials(grid_data)
        
        # 生成高清图片
        print("3. 生成高清拼搭图...")
        image_path = self.generate_high_res_image(grid_data)
        
        # 生成材料报告
        print("4. 生成材料清单报告...")
        materials_path = self.generate_materials_report(materials)
        
        # 生成拼搭指南
        print("5. 生成拼搭指南...")
        guide_path = self.generate_building_instructions(grid_data)
        
        # 生成JSON数据
        print("6. 生成JSON数据...")
        json_path = self.generate_json_data(grid_data, materials)
        
        print("\n" + "=" * 50)
        print("🎉 马里奥乐高拼搭项目生成完成!")
        print("=" * 50)
        print("生成的文件:")
        print(f"  📸 高清拼搭图: {image_path}")
        print(f"  📋 材料清单报告: {materials_path}")
        print(f"  🔧 拼搭指南: {guide_path}")
        print(f"  💾 JSON数据: {json_path}")
        print()
        
        # 显示材料统计
        print("材料统计:")
        total_colored = sum(count for color, count in materials.items() if color != 'white')
        for color, count in sorted(materials.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                color_name = self.color_names_zh.get(color, color)
                percentage = (count / self.total_bricks) * 100
                print(f"  {color_name}: {count:,}块 ({percentage:.1f}%)")
                
        print(f"\n总计有色乐高: {total_colored:,}块")
        print(f"预估成本: ¥{total_colored * 0.5:.2f}")

if __name__ == "__main__":
    generator = LegoMarioGenerator()
    generator.run_complete_generation()