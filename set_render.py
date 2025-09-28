import bpy

# 确保使用的是Cycles渲染引擎
bpy.context.scene.render.engine = 'CYCLES'

# 设置Cycles设备为GPU Compute (AMD HIP RT)
preferences = bpy.context.preferences
cycles_preferences = preferences.addons['cycles'].preferences

# 启用HIP设备（AMD GPU）
cycles_preferences.compute_device_type = 'HIP'

# 获取可用的计算设备并启用所有HIP设备
cycles_preferences.get_devices()
for device in cycles_preferences.devices:
    if device.type == 'HIP':
        device.use = True
        print(f"启用HIP设备: {device.name}")
    else:
        device.use = False

# 应用设备设置到场景
bpy.context.scene.cycles.device = 'GPU'

# 获取Cycles渲染设置
cycles = bpy.context.scene.cycles

# 设置视口渲染参数
cycles.use_preview_adaptive_sampling = True  # 启用自适应采样（Noise Threshold需要此选项）
cycles.preview_adaptive_threshold = 0.150    # Noise Threshold
cycles.preview_samples = 100                 # Max samples

# 设置降噪器
cycles.use_denoising = True
cycles.denoiser = 'OPENIMAGEDENOISE'  # OPEN IMAGE DENOISE

# 设置降噪使用的通道
cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'  # Albedo and Normal

# 设置降噪开始采样
cycles.preview_denoising_start_sample = 8

print("Cycles设置已应用：")
print(f"- 渲染引擎: Cycles")
print(f"- 设备类型: {cycles_preferences.compute_device_type}")
print(f"- 渲染设备: {bpy.context.scene.cycles.device}")
print(f"- Noise Threshold: {cycles.preview_adaptive_threshold}")
print(f"- Max samples: {cycles.preview_samples}")
print(f"- Denoiser: {cycles.denoiser}")
print(f"- Denoising passes: {cycles.denoising_input_passes}")
print(f"- Start sample: {cycles.preview_denoising_start_sample}")

# 列出已启用的设备
enabled_devices = [device.name for device in cycles_preferences.devices if device.use]
print(f"- 已启用的设备: {enabled_devices}")