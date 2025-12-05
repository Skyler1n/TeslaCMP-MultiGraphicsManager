# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import os
import sys
import ctypes

# 简单的兼容层，防止没有TkinterNEW报错
try:
    from TkinterNEW import new
except ImportError:
    class NewModule:
        def NewLabel(self, *args, **kwargs):
            size = kwargs.pop('size', 10)
            kwargs['font'] = ('微软雅黑', size)
            if 'bg' not in kwargs: kwargs['bg'] = '#FFFFFF'
            if 'fg' not in kwargs: kwargs['fg'] = '#000000'
            return tk.Label(*args, **kwargs)
        def NewButton(self, master, text, command):
            f = tk.Frame(master, bg='#FFFFFF')
            b = tk.Button(f, text=text, command=command, bg='#E1E1E1', relief='flat')
            b.pack(fill='both', expand=True)
            return f, b
    new = NewModule()

class GraphicsCardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("多显卡管理器")
        
        # 获取DPI缩放因子，适配高分屏幕
        try:
            # 获取主窗口的DPI
            dpi = ctypes.windll.user32.GetDpiForWindow(self.root.winfo_id())
            # 计算缩放因子（默认DPI为96）
            self.scale_factor = dpi / 96.0
        except:
            # 如果获取失败，使用默认缩放因子1.0
            self.scale_factor = 1.0
        
        # 根据缩放因子调整窗口大小
        width = int(700 * self.scale_factor)
        height = int(550 * self.scale_factor)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.theme_use('vista')
        
        self.root.config(bg='#FFFFFF')
        
        self.graphics_cards = []      
        self.dx_cards = []            
        self.gl_cards = []            
        
        self.create_widgets()
        self.scan_graphics_cards()

    def create_widgets(self):
        # --- 左侧导航栏 ---
        self.tab_bar = tk.Frame(self.root, bg='#FFFFFF', width=200)
        self.tab_bar.place(relx=0, rely=0, relheight=1, relwidth=0.225)
        
        title = new.NewLabel(size=14, text="多显卡管理器")
        title.place(in_=self.tab_bar, relx=0.5, y=48, anchor="n")
        
        def create_tab_btn(text, command, y_pos):
            btn = tk.Button(self.tab_bar, text=text, 
                           bg='#FFFFFF', fg='#000000', font=('微软雅黑', 10),
                           bd=0, highlightthickness=0, relief=tk.FLAT,
                           justify=tk.LEFT, anchor='w', padx=15,
                           command=command)
            btn.place(relx=0, rely=y_pos, relwidth=1, height=48)
            return btn

        self.tab_settings_btn = create_tab_btn("🛠   显卡设置", lambda: self.show_tab("settings"), 0.15)
        self.tab_dx_btn = create_tab_btn("🎮   DirectX 设置", lambda: self.show_tab("dx"), 0.25)
        self.tab_gl_btn = create_tab_btn("🎨   OpenGL 设置", lambda: self.show_tab("gl"), 0.35)
        self.tab_usage_btn = create_tab_btn("📖   使用说明", lambda: self.show_tab("usage"), 0.45)
        self.tab_download_btn = create_tab_btn("💾   驱动下载", lambda: self.show_tab("download"), 0.55)
        self.tab_about_btn = create_tab_btn("⚙️   关于本软件", lambda: self.show_tab("about"), 0.65)
        
        # --- 主内容区域 ---
        self.content_frame = tk.Frame(self.root, bg='#FFFFFF')
        self.content_frame.place(relx=0.25, rely=0, relheight=1, relwidth=0.75)
        
        self.settings_frame = tk.Frame(self.content_frame, bg='#FFFFFF')
        self.setup_settings_ui()
        
        self.dx_frame = tk.Frame(self.content_frame, bg='#FFFFFF')
        self.setup_dx_ui()

        self.gl_frame = tk.Frame(self.content_frame, bg='#FFFFFF')
        self.setup_gl_ui()
        
        self.usage_frame = tk.Frame(self.content_frame, bg='#FFFFFF')
        self.setup_usage_ui()
        
        self.download_frame = tk.Frame(self.content_frame, bg='#FFFFFF')
        self.setup_download_ui()
        
        self.about_frame = tk.Frame(self.content_frame, bg='#FFFFFF')
        self.setup_about_ui()
        
        self.show_tab("settings")

    def setup_settings_ui(self):
        list_frame = tk.Frame(self.settings_frame, bg='#FFFFFF')
        list_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.35)
        
        new.NewLabel(size=12, text="系统中的显卡 (通用)").place(in_=list_frame, relx=0.05, y=5, anchor="nw")
        
        self.card_listbox = tk.Listbox(list_frame, bg='#FFFFFF', fg='#000000', 
                                     selectbackground='#E8F0FE', selectforeground='#000000',
                                     font=('微软雅黑', 10), bd=1, relief=tk.SUNKEN, 
                                     highlightbackground='#CCCCCC', highlightcolor='#0078D7',
                                     activestyle='none')
        self.card_listbox.place(relx=0.05, rely=0.2, relwidth=0.7, relheight=0.7)
        self.card_listbox.bind('<<ListboxSelect>>', self.on_card_select)
        
        new.NewButton(list_frame, text="刷新", command=self.scan_graphics_cards)[0].place(relx=0.78, rely=0.2, relwidth=0.2, relheight=0.2, anchor="nw")
        
        control_frame = tk.Frame(self.settings_frame, bg='#FFFFFF')
        control_frame.place(relx=0.05, rely=0.45, relwidth=0.9, relheight=0.5)
        
        new.NewLabel(size=12, text="显卡设置").place(in_=control_frame, relx=0.05, y=5, anchor="nw")
        
        mode_frame = tk.LabelFrame(control_frame, text="性能模式", bg='#FFFFFF', font=('微软雅黑', 10))
        mode_frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.25)
        
        self.mode_var = tk.IntVar(value=0)
        style = ttk.Style()
        style.configure("Win10.TRadiobutton", background='#FFFFFF', font=('微软雅黑', 10))
        
        ttk.Radiobutton(mode_frame, text="节能", variable=self.mode_var, value=1, style="Win10.TRadiobutton").place(relx=0.1, rely=0.5, anchor="center")
        ttk.Radiobutton(mode_frame, text="高性能", variable=self.mode_var, value=2, style="Win10.TRadiobutton").place(relx=0.4, rely=0.5, anchor="center")
        ttk.Radiobutton(mode_frame, text="未配置", variable=self.mode_var, value=0, style="Win10.TRadiobutton").place(relx=0.7, rely=0.5, anchor="center")
        
        unlock_frame = tk.LabelFrame(control_frame, text="高级设置", bg='#FFFFFF', font=('微软雅黑', 10))
        unlock_frame.place(relx=0.05, rely=0.45, relwidth=0.9, relheight=0.2)
        
        self.unlock_var = tk.BooleanVar(value=False)
        style.configure("Win10.TCheckbutton", background='#FFFFFF', font=('微软雅黑', 10))
        ttk.Checkbutton(unlock_frame, text="解锁计算卡WDDM限制", variable=self.unlock_var, style="Win10.TCheckbutton").place(relx=0.1, rely=0.5, anchor="w")
        
        new.NewButton(control_frame, text="应用设置", command=self.apply_settings)[0].place(relx=0.5, rely=0.9, relwidth=0.3, anchor="s")

    def setup_dx_ui(self):
        list_frame = tk.Frame(self.dx_frame, bg='#FFFFFF')
        list_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.55)
        
        new.NewLabel(size=12, text="支持 DirectX 的显卡").place(in_=list_frame, relx=0.05, y=5, anchor="nw")
        
        self.dx_listbox = tk.Listbox(list_frame, bg='#FFFFFF', fg='#000000', 
                                     selectbackground='#E8F0FE', selectforeground='#000000',
                                     font=('微软雅黑', 10), bd=1, relief=tk.SUNKEN)
        self.dx_listbox.place(relx=0.05, rely=0.15, relwidth=0.7, relheight=0.8)
        
        new.NewButton(list_frame, text="刷新", command=self.scan_dx_cards)[0].place(relx=0.78, rely=0.15, relwidth=0.2, height=30, anchor="nw")
        
        bottom_frame = tk.Frame(self.dx_frame, bg='#FFFFFF')
        bottom_frame.place(relx=0.05, rely=0.65, relwidth=0.9, relheight=0.3)
        
        self.lbl_current_dx = new.NewLabel(size=10, text="当前设置的使用DX渲染的显卡：正在读取...")
        self.lbl_current_dx.place(in_=bottom_frame, relx=0.05, rely=0, anchor="nw")
        
        new.NewButton(bottom_frame, text="设为 DX 高性能 GPU", command=self.apply_dx_settings)[0].place(relx=0.3, rely=0.5, relwidth=0.35, anchor="center")
        
        btn_restore_frame, btn_restore = new.NewButton(bottom_frame, text="还原/清除 DX 设置", command=self.restore_dx_settings)
        btn_restore.config(bg='#FFF0F0', fg='#D00000')
        btn_restore_frame.place(relx=0.75, rely=0.5, relwidth=0.35, anchor="center")
        
        new.NewLabel(size=8, text="* 还原将清空注册表中 HighPerfAdapter 的指定", fg='#888888').place(in_=bottom_frame, relx=0.5, rely=0.85, anchor="center")

    def setup_gl_ui(self):
        list_frame = tk.Frame(self.gl_frame, bg='#FFFFFF')
        list_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.55)
        
        new.NewLabel(size=12, text="可用 OpenGL ICD 驱动").place(in_=list_frame, relx=0.05, y=5, anchor="nw")
        
        self.gl_listbox = tk.Listbox(list_frame, bg='#FFFFFF', fg='#000000', 
                                     selectbackground='#E8F0FE', selectforeground='#000000',
                                     font=('微软雅黑', 10), bd=1, relief=tk.SUNKEN)
        self.gl_listbox.place(relx=0.05, rely=0.15, relwidth=0.7, relheight=0.8)
        
        new.NewButton(list_frame, text="刷新", command=self.scan_gl_cards)[0].place(relx=0.78, rely=0.15, relwidth=0.2, height=30, anchor="nw")
        
        bottom_frame = tk.Frame(self.gl_frame, bg='#FFFFFF')
        bottom_frame.place(relx=0.05, rely=0.65, relwidth=0.9, relheight=0.3)
        
        new.NewButton(bottom_frame, text="强制使用选定 OpenGL 驱动", command=self.apply_gl_settings)[0].place(relx=0.3, rely=0.4, relwidth=0.45, anchor="center")
        
        btn_restore_frame, btn_restore = new.NewButton(bottom_frame, text="还原 OpenGL 默认设置", command=self.restore_gl_settings)
        btn_restore.config(bg='#FFF0F0', fg='#D00000')
        btn_restore_frame.place(relx=0.8, rely=0.4, relwidth=0.35, anchor="center")

        lbl_warn = tk.Label(bottom_frame, text="注意：强制指定会修改全局设置。还原操作将清除全局设置并恢复所有显卡的默认驱动。", 
                           bg='#FFFFFF', fg='#666666', font=('微软雅黑', 8), wraplength=450, justify='center')
        lbl_warn.place(relx=0.5, rely=0.8, anchor="center")

    def setup_usage_ui(self):
        # --- 1. 初始化滚动容器 ---
        # 清理旧控件
        for widget in self.usage_frame.winfo_children():
            widget.destroy()

        content_container = tk.Frame(self.usage_frame, bg='#FFFFFF')
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # 使用 highlightthickness=0 去除边框
        canvas = tk.Canvas(content_container, bg='#FFFFFF', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')
        
        # 布局：滚动条在右，Canvas占满剩余
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建窗口并保存ID
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # --- 核心修复：更精确的宽度计算 ---
        self.wrap_labels = []

        def on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 1. 强制 Frame 宽度跟随 Canvas 变化
            canvas.itemconfig(canvas_window, width=event.width)
            
            # 2. 计算文字换行宽度
            # 解释：总宽 - (卡片外边距40 + 卡片内边距30 + 滚动条20 + 安全冗余10) ≈ 100
            # 之前设置太宽导致了截断
            width = event.width - 110 
            if width < 200: width = 200
            
            for label in self.wrap_labels:
                label.configure(wraplength=width)
        
        canvas.bind("<Configure>", on_canvas_configure)

        def bind_scroll(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_scroll(child)

        # --- 2. UI 组件构建 ---

        def create_header(text, icon):
            """大标题"""
            f = tk.Frame(scrollable_frame, bg='#FFFFFF')
            f.pack(fill='x', padx=20, pady=(25, 10))
            tk.Label(f, text=f"{icon}  {text}", font=('微软雅黑', 13, 'bold'), 
                   bg='#FFFFFF', fg='#333333').pack(side='left')
            bind_scroll(f)

        def create_instruction_card(title, steps):
            """场景卡片"""
            # 外层卡片容器
            card = tk.Frame(scrollable_frame, bg='#F7F9FA', bd=1, relief='solid')
            card.config(highlightbackground="#E1E1E1", highlightthickness=1, relief='flat')
            card.pack(fill='x', padx=20, pady=6)
            
            # 标题栏
            head = tk.Frame(card, bg='#E8F0FE', padx=10, pady=8)
            head.pack(fill='x')
            tk.Label(head, text=title, font=('微软雅黑', 10, 'bold'), 
                   bg='#E8F0FE', fg='#005A9E').pack(anchor='w')
            
            # 内容区
            body = tk.Frame(card, bg='#F7F9FA', padx=15, pady=10)
            body.pack(fill='x')
            
            for step in steps:
                step_f = tk.Frame(body, bg='#F7F9FA')
                step_f.pack(fill='x', pady=2) # fill='x' 确保占满宽度
                
                # 项目符号
                tk.Label(step_f, text="•", font=('微软雅黑', 12, 'bold'), 
                       bg='#F7F9FA', fg='#999999').pack(side='left', anchor='nw')
                
                # 文字内容
                lbl = tk.Label(step_f, text=step, font=('微软雅黑', 9), 
                             bg='#F7F9FA', fg='#444444', justify='left', anchor='w')
                lbl.pack(side='left', padx=(5, 0), fill='x', expand=True) # expand=True 允许文字占据剩余空间
                self.wrap_labels.append(lbl)

            bind_scroll(card)
            bind_scroll(head)
            bind_scroll(body)

        def create_info_block(title, content_dict):
            """信息块"""
            block = tk.Frame(scrollable_frame, bg='#FFFFFF')
            block.pack(fill='x', padx=20, pady=8)
            
            tk.Label(block, text=title, font=('微软雅黑', 10, 'bold'), 
                   bg='#FFFFFF', fg='#333333').pack(anchor='w', pady=(0, 5))
            
            for subtitle, text in content_dict.items():
                row = tk.Frame(block, bg='#FFFFFF')
                row.pack(fill='x', pady=2, padx=10)
                
                if subtitle:
                    tk.Label(row, text=subtitle, font=('微软雅黑', 9, 'bold'), 
                           bg='#F0F0F0', fg='#555555', width=8).pack(side='left', anchor='nw')
                
                lbl = tk.Label(row, text=text, font=('微软雅黑', 9), 
                             bg='#FFFFFF', fg='#666666', justify='left', anchor='w')
                lbl.pack(side='left', padx=(10, 0), fill='x', expand=True)
                self.wrap_labels.append(lbl)
            
            bind_scroll(block)

        def create_warning_box(text):
            """警告框"""
            box = tk.Frame(scrollable_frame, bg='#FFF8E1', bd=1, relief='solid')
            box.config(highlightbackground="#FFD54F", highlightthickness=1, relief='flat')
            box.pack(fill='x', padx=20, pady=15)
            
            inner = tk.Frame(box, bg='#FFF8E1', padx=15, pady=10)
            inner.pack(fill='x')
            
            tk.Label(inner, text="⚠️ 注意事项", font=('微软雅黑', 9, 'bold'), 
                   bg='#FFF8E1', fg='#B00020').pack(anchor='w', pady=(0, 5))
            
            lbl = tk.Label(inner, text=text, font=('微软雅黑', 9), 
                         bg='#FFF8E1', fg='#5D4037', justify='left', anchor='w')
            lbl.pack(fill='x', expand=True)
            self.wrap_labels.append(lbl)
            
            bind_scroll(box)
            bind_scroll(inner)

        # --- 3. 填充内容 ---
        
        tk.Frame(scrollable_frame, bg='#FFFFFF', height=5).pack()
        
        top_lbl = tk.Label(scrollable_frame, text="首先请尝试使用“显卡设置”页面的选项。\n如果无效再设置DirectX、OpenGL优先显卡和参考以下方案。", 
                         font=('微软雅黑', 10), bg='#FFFFFF', fg='#666666', pady=5, justify='left', anchor='w')
        top_lbl.pack(fill='x', padx=20)
        self.wrap_labels.append(top_lbl)

        create_header("常见硬件搭配设置", "🛠️")
        
        create_instruction_card("场景 1: Intel 核显 (接显示器) + NVIDIA 计算卡", [
            "设置 Intel 核显为：节能模式",
            "设置 NVIDIA 计算卡为：高性能模式"
        ])
        
        create_instruction_card("场景 2: NVIDIA 独显 (接显示器) + NVIDIA 计算卡", [
            "设置 NVIDIA 独显 (亮机卡) 为：节能模式",
            "设置 NVIDIA 计算卡为：高性能模式"
        ])
        
        create_instruction_card("场景 3: AMD 独显 (接显示器) + NVIDIA 计算卡", [
            "设置 AMD 独显为：高性能模式",
            "设置 NVIDIA 计算卡为：节能模式\n\n"
            "然后使用本软件的DirectX、OpenGL设置指定调用的显卡\n"
            "Win11 可以在显示设置 > 图形设置中手动添加应用并指定GPU。"
        ])

        create_header("系统版本差异", "💻")
        create_info_block("如何指定 GPU 优先级：", {
            "Win 11": "在“系统设置 > 显示设置 > 图形设置”中，手动添加游戏/应用，\n并指定优先调用的 GPU。",
            "Win 10": "使用本软件的“DirectX 设置”和“OpenGL 设置”强制指定显卡。"
        })

        create_header("特殊硬件说明", "🔩")
        create_info_block("Tesla 专业计算卡 (M40, P40, P100 等)：", {
            "": "必须勾选“解锁计算卡 WDDM 限制”选项，否则无法正常调用。"
        })
        
        create_info_block("CMP 矿卡 (P106, 30HX, 40HX 等)：", {
            "魔改驱动": "使用雨糖等魔改驱动：不需要勾选解锁 WDDM。",
            "官方驱动": "使用 41x 等官方驱动：必须勾选解锁 WDDM。"
        })

        create_header("测试与排错", "🩺")
        
        test_lbl = tk.Label(scrollable_frame, text="• 推荐使用图吧工具箱的 FurMark和FurMark2 (甜甜圈) 进行烤机和调用测试。\n• 若无法调用，请检查 NVIDIA 控制面板 3D 设置中的 OpenGL 渲染 GPU 选项。", 
                font=('微软雅黑', 9), bg='#FFFFFF', fg='#444444', justify='left', anchor='w', padx=25)
        test_lbl.pack(fill='x')
        self.wrap_labels.append(test_lbl)

        create_warning_box(
            "1. 若显卡调用正常，不建议修改 NVIDIA 控制面板中的选项。\n特别是“PhysX”或“使用高性能NVIDIA处理器”等设置，通常是负优化。\n"
            "2. 强制修改 DX/GL 设置如遇问题请在对应页面点击“还原”按钮。"
        )

        tk.Frame(scrollable_frame, bg='#FFFFFF', height=30).pack()

    def setup_download_ui(self):
        # --- 1. 初始化滚动容器 ---
        # 清理旧控件
        for widget in self.download_frame.winfo_children():
            widget.destroy()

        content_container = tk.Frame(self.download_frame, bg='#FFFFFF')
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # 使用 highlightthickness=0 去除边框
        canvas = tk.Canvas(content_container, bg='#FFFFFF', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')
        
        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建窗口并保存ID用于调整宽度
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # 动态调整列表
        self.wrap_labels = []

        def on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 强制内容宽度等于窗口宽度
            canvas.itemconfig(canvas_window, width=event.width)
            
            # 计算换行宽度 (总宽 - 左右边距 - 滚动条)
            width = event.width - 40
            if width < 200: width = 200
            for label in self.wrap_labels:
                label.configure(wraplength=width)
        
        canvas.bind("<Configure>", on_canvas_configure)

        def bind_scroll(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_scroll(child)

        # --- 2. UI 组件样式设计 ---
        
        def create_header(text, icon):
            """大标题"""
            f = tk.Frame(scrollable_frame, bg='#FFFFFF')
            f.pack(fill='x', padx=15, pady=(20, 10))
            tk.Label(f, text=f"{icon}  {text}", font=('微软雅黑', 12, 'bold'), 
                   bg='#FFFFFF', fg='#333333').pack(side='left')
            bind_scroll(f)

        def create_link_box(title, url, note=None):
            """下载链接块"""
            box = tk.Frame(scrollable_frame, bg='#F0F4F8', bd=0)
            box.pack(fill='x', padx=15, pady=4)
            
            tk.Label(box, text=title, font=('微软雅黑', 10, 'bold'), 
                   bg='#F0F4F8', fg='#333333').pack(anchor='w', padx=10, pady=(8, 2))
            
            link_f = tk.Frame(box, bg='#F0F4F8')
            link_f.pack(fill='x', padx=10, pady=(0, 8))
            
            link = tk.Label(link_f, text="点击下载", font=('微软雅黑', 9, 'bold'), 
                          bg='#0078D7', fg='#FFFFFF', padx=8, pady=2, cursor='hand2')
            link.pack(side='left')
            link.bind("<Button-1>", lambda e: self.open_url(url))
            
            if note:
                tk.Label(link_f, text=note, font=('微软雅黑', 9), 
                       bg='#F0F4F8', fg='#D00000').pack(side='left', padx=(10, 0))
            bind_scroll(box)

        def create_driver_row(ver, core_support, desc):
            """
            驱动版本行 (新布局)
            第一行：[版本号]  [支持的核心范围]
            第二行：具体描述
            """
            row = tk.Frame(scrollable_frame, bg='#FFFFFF')
            row.pack(fill='x', padx=15, pady=8) # 增加一点垂直间距
            
            # --- 第一行容器 ---
            top_line = tk.Frame(row, bg='#FFFFFF')
            top_line.pack(fill='x', anchor='w')
            
            # 1. 版本号 (灰色背景胶囊)
            tk.Label(top_line, text=ver, font=('微软雅黑', 10, 'bold'), 
                   bg='#E1E1E1', fg='#000000', width=8).pack(side='left')
            
            # 2. 核心支持 (蓝色文字，紧跟版本号)
            tk.Label(top_line, text=core_support, font=('微软雅黑', 9, 'bold'), 
                   bg='#FFFFFF', fg='#0078D7').pack(side='left', padx=(10, 0))
            
            # --- 第二行：描述 ---
            desc_lbl = tk.Label(row, text=desc, font=('微软雅黑', 9), 
                              bg='#FFFFFF', fg='#555555', justify='left', anchor='w')
            desc_lbl.pack(fill='x', pady=(4, 0)) # 文字与标题有一点间距
            
            self.wrap_labels.append(desc_lbl)
            
            # 底部细分割线
            tk.Frame(scrollable_frame, bg='#EEEEEE', height=1).pack(fill='x', padx=15)
            
            bind_scroll(row)
            bind_scroll(top_line)

        def create_core_row(code, info):
            """核心代号行"""
            row = tk.Frame(scrollable_frame, bg='#FFFFFF')
            row.pack(fill='x', padx=15, pady=5)
            tk.Label(row, text=f"● {code}", font=('微软雅黑', 9, 'bold'), 
                   bg='#FFFFFF', fg='#0066CC').pack(anchor='w')
            info_lbl = tk.Label(row, text=info, font=('微软雅黑', 9), 
                              bg='#FFFFFF', fg='#444444', justify='left', anchor='w')
            info_lbl.pack(fill='x', padx=(15, 0))
            self.wrap_labels.append(info_lbl)
            bind_scroll(row)

        # --- 3. 填充内容 ---
        
        tk.Frame(scrollable_frame, bg='#FFFFFF', height=10).pack()

        # [资源下载]
        create_header("资源下载", "💾")
        create_link_box("Skyler1n 官方整合驱动，NV官方驱动签名 (Tesla+GeForce首选)", "https://www.123865.com/s/mHIrVv-9Q0OA?pwd=Ox1f#", "提取码: Ox1f，适合绝大多数Tesla计算卡和其他N卡共存驱动。")
        create_link_box(f"RainCandy 雨糖魔改驱动，双签名模式 (P106/30HX/40HX首选)", "https://raincandy.tech/nvcmpgpu/", "对CMP系列显卡解锁了WDDM限制，有可能无法通过反作弊系统。")

        # [官方驱动]
        create_header("驱动说明", "📝")
        
        # 数据结构改为: (版本号, 核心支持范围, 详细描述)
        drivers = [
            ("388.19", "GF-GP核心   GeForce，Quadro，CMP，Tesla驱动共存", "双卡只能强制调用，P106/30HX等CMP系列显卡不锁WDDM。"),
            ("411.31", "GK-TU核心   GeForce，Quadro，CMP，Tesla驱动共存", "P106/30HX等CMP系列显卡不锁WDDM。"),
            ("417.22", "GK-TU核心   GeForce，Quadro，CMP驱动并存", "P106/30HX等CMP系列显卡最后一个不锁WDDM的官方驱动。"),
            ("472.50", "GK-GA核心   GeForce，Quadro，Tesla驱动并存", "最后一个兼容GK 开普勒 Kepler架构的共存的官方驱动。"),
            ("537.13", "GM-AD核心   GeForce，Quadro，Tesla驱动并存", "GeForce GTX750Ti，Quadro K620等初代麦克斯韦可以正常睡眠唤醒的官驱。"),
            ("537.99", "GM-AD核心   Quadro，Tesla驱动并存", "Quadro K620等初代麦克斯韦最后一个可以正常睡眠唤醒的官驱。"),
            ("546.12", "GM-AD核心   GeForce，Quadro，Tesla驱动并存", "QQNT最后一个无异常占用GPU BUG的官驱（可能QQNT后续已经修复）。"),
            ("576.57", "GM-GB核心   GeForce，Quadro，Tesla驱动并存", "NV提供的最后一版全硬件共存驱动。"),
        ]
        
        for ver, core, desc in drivers:
            create_driver_row(ver, core, desc)

        # [核心说明]
        create_header("核心代号", "🔍")
        
        cores = [
            ("GF 费米 Fermi", "GTX 400/500 系列，少量 GT610/710，Quadro 600 等"),
            ("GK 开普勒 Kepler", "GTX 600/700(绝大部分) 系列，Quadro 410/K420/K600，Tesla K20c 等"),
            ("GM 麦克斯韦 Maxwell", "GTX 750(Ti)/900 系列，Quadro K620/M600，Tesla M40 等"),
            ("GP 帕斯卡 Pascal", "GTX 10 系列，Quadro P400/P600/P620，Tesla P40/P100 等"),
            ("GV 伏打 Volta", "Tesla V100 等高端计算卡"),
            ("TU 图灵 Turing", "RTX 20 系列，GTX 16 系列"),
            ("GA 安培 Ampere", "RTX 30 系列"),
            ("AD 埃达 Ada Lovelace", "RTX 40 系列"),
            ("GB 布莱克 Blackwell", "RTX 50 系列"),
        ]
        
        for c, i in cores:
            create_core_row(c, i)

        tk.Frame(scrollable_frame, bg='#FFFFFF', height=30).pack()

    def open_url(self, url):
        # 使用ctypes调用系统浏览器打开链接
        ctypes.windll.shell32.ShellExecuteW(None, "open", url, None, None, 1)
    
    def setup_about_ui(self):
        # 清理旧控件
        for widget in self.about_frame.winfo_children():
            widget.destroy()

        # 主容器：白色背景，内容居中
        main_container = tk.Frame(self.about_frame, bg='#FFFFFF')
        main_container.pack(fill=tk.BOTH, expand=True)

        # 内容居中容器 (防止在大屏幕上内容太散)
        center_frame = tk.Frame(main_container, bg='#FFFFFF')
        center_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.85)

        # --- 1. 头部信息 (图标/标题/版本) ---
        header_frame = tk.Frame(center_frame, bg='#FFFFFF')
        header_frame.pack(fill='x', pady=(0, 20))

        # 软件标题
        tk.Label(header_frame, text="多显卡管理器", font=('微软雅黑', 22, 'bold'), 
                 bg='#FFFFFF', fg='#333333').pack()
        
        # 版本号 (胶囊样式)
        ver_frame = tk.Frame(header_frame, bg='#E8F0FE', padx=10, pady=2)
        ver_frame.pack(pady=(5, 0))
        tk.Label(ver_frame, text="Version 1.0", font=('微软雅黑', 9, 'bold'), 
                 bg='#E8F0FE', fg='#005A9E').pack()

        # 分割线
        ttk.Separator(center_frame, orient='horizontal').pack(fill='x', pady=20)

        # --- 2. 作者与链接区域 ---
        info_frame = tk.Frame(center_frame, bg='#FFFFFF')
        info_frame.pack(fill='x', pady=(0, 20))

        def create_info_row(label_text, value_text, url=None):
            row = tk.Frame(info_frame, bg='#FFFFFF')
            row.pack(pady=4)
            
            # 标签
            tk.Label(row, text=label_text, font=('微软雅黑', 10), 
                     bg='#FFFFFF', fg='#666666').pack(side='left')
            
            # 值 (如果是链接则特殊处理)
            if url:
                val_lbl = tk.Label(row, text=value_text, font=('微软雅黑', 10, 'bold'), 
                                 bg='#FFFFFF', fg='#0066CC', cursor='hand2')
                val_lbl.bind("<Button-1>", lambda e: self.open_url(url))
                # 增加下划线效果
                f = tk.font.Font(val_lbl, val_lbl.cget("font"))
                f.configure(underline=True)
                val_lbl.configure(font=f)
            else:
                val_lbl = tk.Label(row, text=value_text, font=('微软雅黑', 10, 'bold'), 
                                 bg='#FFFFFF', fg='#333333')
            
            val_lbl.pack(side='left', padx=(5, 0))

        create_info_row("软件作者：", "Skyler1n")
        create_info_row("GitHub 主页：", "@Skyler1n", "https://github.com/Skyler1n")
        create_info_row("开源项目：", "TeslaCMP-MultiGraphicsManager", "https://github.com/Skyler1n/TeslaCMP-MultiGraphicsManager")

        # --- 3. 功能列表区域 ---
        feature_frame = tk.Frame(center_frame, bg='#F9F9F9', padx=20, pady=15)
        feature_frame.pack(fill='x', pady=(0, 20))
        
        # 功能标题
        tk.Label(feature_frame, text="软件主要功能", font=('微软雅黑', 11, 'bold'), 
                 bg='#F9F9F9', fg='#333333').pack(anchor='w', pady=(0, 10))

        features = [
            "设置显卡“节能/高性能”模式，以便让系统自动调用",
            "解锁计算卡 (Tesla/CMP) 的WDDM图形渲染限制",
            "更改首选的 DirectX 显卡",
            "更改首选的 OpenGL 显卡",
        ]

        for ft in features:
            f_row = tk.Frame(feature_frame, bg='#F9F9F9')
            f_row.pack(anchor='w', pady=2)
            # 勾选图标
            tk.Label(f_row, text="✓", font=('微软雅黑', 10, 'bold'), 
                     bg='#F9F9F9', fg='#0078D7').pack(side='left')
            # 文本
            tk.Label(f_row, text=ft, font=('微软雅黑', 10), 
                     bg='#F9F9F9', fg='#555555').pack(side='left', padx=(8, 0))

        # --- 4. 底部版权 ---
        footer_frame = tk.Frame(center_frame, bg='#FFFFFF')
        footer_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(footer_frame, text="数据来源参考: nethe-GitHub", 
                 font=('微软雅黑', 8), bg='#FFFFFF', fg='#999999').pack()
        tk.Label(footer_frame, text="Copyright © 2024 Skyler1n. All Rights Reserved.", 
                 font=('微软雅黑', 8), bg='#FFFFFF', fg='#999999').pack(pady=(2, 0))

    def show_tab(self, tab_name):
        for frame in [self.settings_frame, self.dx_frame, self.gl_frame, self.usage_frame, self.download_frame, self.about_frame]:
            frame.pack_forget()
        
        btns = [self.tab_settings_btn, self.tab_dx_btn, self.tab_gl_btn, self.tab_usage_btn, self.tab_download_btn, self.tab_about_btn]
        for btn in btns:
            btn.config(bg='#FFFFFF', fg='#000000')
            
        target_frame = None
        target_btn = None
        
        if tab_name == "settings":
            target_frame = self.settings_frame
            target_btn = self.tab_settings_btn
        elif tab_name == "dx":
            target_frame = self.dx_frame
            target_btn = self.tab_dx_btn
            self.scan_dx_cards()
        elif tab_name == "gl":
            target_frame = self.gl_frame
            target_btn = self.tab_gl_btn
            self.scan_gl_cards()
        elif tab_name == "usage":
            target_frame = self.usage_frame
            target_btn = self.tab_usage_btn
        elif tab_name == "download":
            target_frame = self.download_frame
            target_btn = self.tab_download_btn
        elif tab_name == "about":
            target_frame = self.about_frame
            target_btn = self.tab_about_btn
            
        if target_frame:
            target_frame.pack(fill=tk.BOTH, expand=True)
        if target_btn:
            target_btn.config(bg='#CCE4F7', fg='#0078D7')

    # ================= 通用功能 =================
    def scan_graphics_cards(self):
        self.graphics_cards = []
        self.card_listbox.delete(0, tk.END)
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("000"):
                            subkey_path = reg_path + "\\" + subkey_name
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path) as subkey:
                                try:
                                    driver_desc = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                                    self.graphics_cards.append((subkey_name, driver_desc))
                                    self.card_listbox.insert(tk.END, driver_desc)
                                except FileNotFoundError: pass
                    except OSError: break
                    i += 1
        except Exception: pass

    def on_card_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            card_id, card_name = self.graphics_cards[index]
            self.load_card_settings(card_id)

    def load_card_settings(self, card_id):
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\\" + card_id
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                try:
                    val = winreg.QueryValueEx(key, "EnableMsHybrid")[0]
                    self.mode_var.set(1 if val == 6 else (2 if val == 1 else 0))
                except: self.mode_var.set(0)
                try:
                    feat = winreg.QueryValueEx(key, "GridLicensedFeatures")[0]
                    atype = winreg.QueryValueEx(key, "AdapterType")[0]
                    self.unlock_var.set(feat == 7 and atype == 1)
                except: self.unlock_var.set(False)
        except: pass

    def apply_settings(self):
        selection = self.card_listbox.curselection()
        if not selection: return
        index = selection[0]
        card_id, card_name = self.graphics_cards[index]
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\\" + card_id
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                mode = self.mode_var.get()
                if mode == 0:
                    try: winreg.DeleteValue(key, "EnableMsHybrid")
                    except: pass
                else:
                    winreg.SetValueEx(key, "EnableMsHybrid", 0, winreg.REG_DWORD, 6 if mode == 1 else 1)
                if self.unlock_var.get():
                    winreg.SetValueEx(key, "GridLicensedFeatures", 0, winreg.REG_DWORD, 7)
                    winreg.SetValueEx(key, "AdapterType", 0, winreg.REG_DWORD, 1)
                else:
                    try: winreg.DeleteValue(key, "GridLicensedFeatures")
                    except: pass
                    try: winreg.DeleteValue(key, "AdapterType")
                    except: pass
            messagebox.showinfo("成功", "设置已应用")
        except Exception as e: messagebox.showerror("错误", str(e))

    # ================= DX 功能 =================
    
    def find_pci_location(self, matching_id):
        # 修正：只提取 VEN_xx & DEV_xx & SUBSYS_xx
        pci_root_path = r"SYSTEM\CurrentControlSet\Enum\PCI"
        target_driver_val = "{4d36e968-e325-11ce-bfc1-08002be10318}\\" + matching_id
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, pci_root_path) as pci_root:
                i = 0
                while True:
                    try:
                        ven_key_name = winreg.EnumKey(pci_root, i)
                        ven_path = pci_root_path + "\\" + ven_key_name
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ven_path) as ven_key:
                            j = 0
                            while True:
                                try:
                                    inst_key_name = winreg.EnumKey(ven_key, j)
                                    inst_path = ven_path + "\\" + inst_key_name
                                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, inst_path) as inst_key:
                                        try:
                                            driver_val = winreg.QueryValueEx(inst_key, "Driver")[0]
                                            if driver_val.lower() == target_driver_val.lower():
                                                parts = ven_key_name.split('&')
                                                ven = dev = subsys = ""
                                                for part in parts:
                                                    if part.startswith("VEN_"): ven = part.split('_')[1]
                                                    elif part.startswith("DEV_"): dev = part.split('_')[1]
                                                    elif part.startswith("SUBSYS_"): subsys = part.split('_')[1]
                                                if ven and dev and subsys:
                                                    return f"{ven}&{dev}&{subsys}"
                                        except FileNotFoundError: pass
                                except OSError: break
                                j += 1
                    except OSError: break
                    i += 1
        except Exception: pass
        return None

    def scan_dx_cards(self):
        self.dx_cards = []
        self.dx_listbox.delete(0, tk.END)
        self.lbl_current_dx.config(text="当前设置的使用DX渲染的显卡：正在读取...")
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("000"):
                            subkey_path = reg_path + "\\" + subkey_name
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path) as subkey:
                                try:
                                    matching_id = winreg.QueryValueEx(subkey, "MatchingDeviceId")[0]
                                    driver_desc = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                                    pci_location = self.find_pci_location(subkey_name)
                                    if pci_location:
                                        self.dx_cards.append((driver_desc, subkey_path, pci_location))
                                        self.dx_listbox.insert(tk.END, driver_desc)
                                except FileNotFoundError: pass
                    except OSError: break
                    i += 1
        except Exception: pass
            
        current_adapter_name = "系统默认 / 未配置"
        try:
            dx_pref_path = r"Software\Microsoft\DirectX\UserGpuPreferences"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, dx_pref_path) as key:
                val = winreg.QueryValueEx(key, "DirectXUserGlobalSettings")[0]
                if "HighPerfAdapter=" in val:
                    parts = val.split(';')
                    for part in parts:
                        if part.startswith("HighPerfAdapter="):
                            current_id = part.split('=')[1].lower()
                            for name, path, pid in self.dx_cards:
                                if pid.lower() in current_id or current_id in pid.lower():
                                    current_adapter_name = name
                                    break
        except FileNotFoundError: pass
        self.lbl_current_dx.config(text=f"当前设置的使用DX渲染的显卡：{current_adapter_name}")

    def apply_dx_settings(self):
        selection = self.dx_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一张显卡")
            return
        idx = selection[0]
        name, reg_path, pci_id = self.dx_cards[idx]
        dx_pref_path = r"Software\Microsoft\DirectX\UserGpuPreferences"
        try:
            try: key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, dx_pref_path, 0, winreg.KEY_ALL_ACCESS)
            except FileNotFoundError: key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, dx_pref_path)
            with key:
                try:
                    current_val = winreg.QueryValueEx(key, "DirectXUserGlobalSettings")[0]
                    swap_val = "1" if "SwapEffectUpgradeEnable=1" in current_val else "0"
                except FileNotFoundError: swap_val = "0"
                # 修正顺序: HighPerfAdapter在前
                new_val = f"HighPerfAdapter={pci_id};SwapEffectUpgradeEnable={swap_val};"
                winreg.SetValueEx(key, "DirectXUserGlobalSettings", 0, winreg.REG_SZ, new_val)
            self.scan_dx_cards()
            messagebox.showinfo("成功", f"已应用 DX 设置:\n{name}")
        except Exception as e: messagebox.showerror("错误", str(e))

    def restore_dx_settings(self):
        if not messagebox.askyesno("确认", "确定要清除 DirectX 的强制显卡设置吗？"): return
        dx_pref_path = r"Software\Microsoft\DirectX\UserGpuPreferences"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, dx_pref_path, 0, winreg.KEY_ALL_ACCESS)
            with key:
                try:
                    current_val = winreg.QueryValueEx(key, "DirectXUserGlobalSettings")[0]
                    new_val = "SwapEffectUpgradeEnable=1;" if "SwapEffectUpgradeEnable=1" in current_val else "SwapEffectUpgradeEnable=0;"
                    winreg.SetValueEx(key, "DirectXUserGlobalSettings", 0, winreg.REG_SZ, new_val)
                    messagebox.showinfo("成功", "DirectX 设置已还原。")
                except FileNotFoundError: pass
            self.scan_dx_cards()
        except Exception as e: messagebox.showerror("错误", f"还原失败: {str(e)}")

    # ================= OpenGL 功能 =================

    def scan_gl_cards(self):
        self.gl_cards = []
        self.gl_listbox.delete(0, tk.END)
        reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("000"):
                            subkey_path = reg_path + "\\" + subkey_name
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path) as subkey:
                                dll, wow = None, None
                                try: dll = winreg.QueryValueEx(subkey, "OpenGLDriverName")[0]
                                except: 
                                    try: dll = winreg.QueryValueEx(subkey, "_OpenGLDriverName")[0]
                                    except: pass
                                try: wow = winreg.QueryValueEx(subkey, "OpenGLDriverNameWow")[0]
                                except:
                                    try: wow = winreg.QueryValueEx(subkey, "_OpenGLDriverNameWow")[0]
                                    except: pass
                                if dll:
                                    try:
                                        desc = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                                        self.gl_cards.append((desc, subkey_path, dll, wow))
                                        self.gl_listbox.insert(tk.END, f"{desc} ({dll})")
                                    except: pass
                    except OSError: break
                    i += 1
        except Exception: pass

    def apply_gl_settings(self):
        selection = self.gl_listbox.curselection()
        if not selection: return
        idx = selection[0]
        sel_name, sel_reg_path, sel_dll, sel_dll_wow = self.gl_cards[idx]
        if not messagebox.askyesno("确认", f"确定强制 OpenGL 驱动为：\n{sel_name}\n这将修改全局注册表。"): return
        
        gl_global_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\OpenGLDrivers\MSOGL"
        try:
            key64 = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, gl_global_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
            with key64:
                # 写入全局设置，路径直接写入 REG_SZ
                winreg.SetValueEx(key64, "DLL", 0, winreg.REG_SZ, sel_dll)
                winreg.SetValueEx(key64, "DriverVersion", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key64, "Version", 0, winreg.REG_DWORD, 2)
                winreg.SetValueEx(key64, "Flags", 0, winreg.REG_DWORD, 3)
            
            if sel_dll_wow:
                key32 = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, gl_global_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_32KEY)
                with key32:
                    winreg.SetValueEx(key32, "DLL", 0, winreg.REG_SZ, sel_dll_wow)
                    winreg.SetValueEx(key32, "DriverVersion", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key32, "Version", 0, winreg.REG_DWORD, 2)
                    winreg.SetValueEx(key32, "Flags", 0, winreg.REG_DWORD, 3)

            # 屏蔽单卡设置
            for name, path, dll, dll_wow in self.gl_cards:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                    winreg.SetValueEx(key, "_OpenGLDriverName", 0, winreg.REG_SZ, dll)
                    if dll_wow: winreg.SetValueEx(key, "_OpenGLDriverNameWow", 0, winreg.REG_SZ, dll_wow)
                    try: winreg.DeleteValue(key, "OpenGLDriverName")
                    except: pass
                    try: winreg.DeleteValue(key, "OpenGLDriverNameWow")
                    except: pass
            
            messagebox.showinfo("成功", "已强制指定 OpenGL 驱动。")
            self.scan_gl_cards()
        except Exception as e: messagebox.showerror("错误", str(e))

    def restore_gl_settings(self):
        if not messagebox.askyesno("确认", "确定要还原 OpenGL 设置吗？"): return
        gl_global_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\OpenGLDrivers\MSOGL"
        try:
            # 删除全局键
            try: winreg.DeleteKeyEx(winreg.HKEY_LOCAL_MACHINE, gl_global_path, winreg.KEY_WOW64_64KEY, 0)
            except FileNotFoundError: pass # 键不存在则忽略
            try: winreg.DeleteKeyEx(winreg.HKEY_LOCAL_MACHINE, gl_global_path, winreg.KEY_WOW64_32KEY, 0)
            except FileNotFoundError: pass

            # 恢复单卡设置
            reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            restored_count = 0
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("000"):
                            subkey_path = reg_path + "\\" + subkey_name
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY) as subkey:
                                try:
                                    # 恢复主驱动
                                    val = winreg.QueryValueEx(subkey, "_OpenGLDriverName")[0]
                                    winreg.SetValueEx(subkey, "OpenGLDriverName", 0, winreg.REG_SZ, val)
                                    winreg.DeleteValue(subkey, "_OpenGLDriverName")
                                    restored_count += 1
                                except FileNotFoundError: pass
                                
                                try:
                                    # 恢复Wow64驱动
                                    val_wow = winreg.QueryValueEx(subkey, "_OpenGLDriverNameWow")[0]
                                    winreg.SetValueEx(subkey, "OpenGLDriverNameWow", 0, winreg.REG_SZ, val_wow)
                                    winreg.DeleteValue(subkey, "_OpenGLDriverNameWow")
                                except FileNotFoundError: pass
                    except OSError: break
                    i += 1
            messagebox.showinfo("成功", f"OpenGL 设置已还原。\n共恢复了 {restored_count} 处配置。")
            self.scan_gl_cards()
        except Exception as e: messagebox.showerror("错误", f"还原 GL 设置失败: {str(e)}")

if __name__ == "__main__":
    # 设置DPI感知，适配高分屏幕
    try:
        # 对于Windows 8.1及以上，设置PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        try:
            # 对于Windows 7及以上，设置PROCESS_SYSTEM_DPI_AWARE
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass
    
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()
    
    # 获取程序运行时的目录
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        app_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        app_path = os.path.dirname(os.path.abspath(__file__))
    
    # 构建图标文件的完整路径
    icon_path = os.path.join(app_path, "ic_launcher.ico")
    
    root = tk.Tk()
    # 设置窗口图标
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"无法加载图标: {e}")
    
    app = GraphicsCardManager(root)
    root.mainloop()