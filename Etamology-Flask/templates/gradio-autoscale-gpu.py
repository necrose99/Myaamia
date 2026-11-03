import os
import sys
import platform
import multiprocessing
import subprocess
import shutil

def probe_silicon_and_memory():
    """
    Automagically maps total host infrastructure limits. Accommodates constraints
    ranging from consumer laptops (8GB RAM) up to donated enterprise cluster platforms 
    featuring multi-terabyte system memory arrays and specialized AI accelerator blocks.
    """
    sys_platform = sys.platform
    os_name = platform.system()
    
    # --------------------------------------------------------------------------
    # A. METRIC TON CAPACITY PROBING (Scale-Agnostic System RAM Verification)
    # --------------------------------------------------------------------------
    total_ram_gb = 16.0  # Default safe engineering constant fallback
    try:
        if sys_platform == "linux":
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if "MemTotal" in line:
                        total_ram_gb = int(line.split()) / (1024 * 1024)
                        break
        elif sys_platform == "win32":
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total_ram_gb = stat.ullTotalPhys / (1024 * 1024 * 1024)
    except Exception:
        pass

    # Elastic Context & Batch Adjustment Matrix based on RAM boundaries
    # Dynamically stretches from consumer laptops up to Massive HPC infrastructure allocations
    if total_ram_gb <= 12.0:
        # Micro-scale profile (e.g., 8GB laptop, local testing constraints)
        context_window = 1024
        batch_size = 8
        ram_tier = f"⚠️ Low-Tier Footprint ({total_ram_gb:.1f}GB RAM). Context downscaled to 1K to protect host layers."
    elif total_ram_gb < 32.0:
        # Mid-scale footprint (Standard workstations, average cloud runtime spaces)
        context_window = 2048
        batch_size = 32
        ram_tier = f"🟢 Desktop/Mid-Tier Profile ({total_ram_gb:.1f}GB RAM). Context locked at standard 2K."
    elif total_ram_gb < 256.0:
        # Professional Engineering Tier (High-end workstations with 96GB/128GB/256GB RAM profiles)
        context_window = 4096
        batch_size = 64
        ram_tier = f"🔥 Enterprise Workstation Tier ({total_ram_gb:.1f}GB RAM). Context scaling upward to 4K tokens."
    else:
        # Enterprise Cluster Environment / Massive HPC Node Tier (From 256GB up into multi-Terabyte domains)
        context_window = 16384
        batch_size = 256
        ram_tier = f"🚀 High-Performance Compute (HPC) Super-Node Tier ({total_ram_gb / 1024:.2f} TB RAM). Scaling context to maximum 16K allocation."

    # --------------------------------------------------------------------------
    # B. DETAILED HARDWARE ARCHITECTURE MATRIX SCANNING
    # --------------------------------------------------------------------------
    profile = {
        "backend": "Standard CPU (Generic GGML)",
        "ngl": 0,
        "threads": max(1, multiprocessing.cpu_count() - 2),
        "flags": [],
        "env_vars": {},
        "context_window": context_window,
        "batch_size": batch_size,
        "notes": f"Host Kernel: {os_name}. Ram Info: {ram_tier}"
    }

    # 1. Cloud Infrastructure Priority Interception (Hugging Face Hosting Tiers)
    if "SPACE_ID" in os.environ:
        if shutil.which("nvidia-smi") or os.path.exists("/usr/bin/nvidia-smi"):
            profile.update({"backend": "Hugging Face Spaces (Dedicated Paid GPU Server)", "ngl": 99, "threads": 1})
            return profile
        else:
            profile.update({"backend": "Hugging Face Spaces (Free CPU Sandbox Shared-RAM)", "ngl": 0, "context_window": 1024})
            return profile

    # 2. Apple Silicon M-Series Architectures (M1/M2/M3/M4 Pro/Max/Ultra Unified Fabrics)
    if sys_platform == "darwin" and platform.machine() == "arm64":
        profile.update({
            "backend": "Apple Silicon Unified Memory Layout",
            "ngl": 99,  # Metal handles complete model layers natively within its unified RAM blocks
            "threads": 1,
            "flags": ["--gpm", "1"] # Enable Metal memory pools mapping optimizations
        })
        return profile

    # 3. Axelera AI Edge-Computing Hardware (Voyager SDK Matrix Blocks)
    if os.path.exists("/opt/axelera") or os.path.exists("/usr/lib/libvoyager.so") or "VOYAGER_SDK_PATH" in os.environ:
        profile.update({
            "backend": "Axelera AI Voyager NPU Core Accelerator",
            "ngl": 99,
            "threads": 1,
            "flags": ["--npu", "0", "--backend", "axelera"]
        })
        return profile

    # 4. Intel Core OpenVINO Co-Processing Layer (Dedicated Hardware NPU Devices)
    if "INTEL_OPENVINO_DIR" in os.environ or os.path.exists("/opt/intel/openvino") or shutil.which("benchmark_app"):
        profile.update({
            "backend": "Intel OpenVINO Core (NPU Accelerated Processing Network)",
            "ngl": 99,
            "env_vars": {"GGML_OPENVINO_DEVICE": "NPU"},
            "flags": ["--openvino-device", "NPU"]
        })
        return profile

    # 5. Intel oneAPI Unified SYCL Hardware Drivers (Arc GPUs / Built-in Processing NPUs)
    if "ONEAPI_ROOT" in os.environ or shutil.which("sycl-ls"):
        try:
            sycl_devices = subprocess.check_output(["sycl-ls"], text=True).lower()
            if "npu" in sycl_devices:
                profile.update({"backend": "Intel SYCL (NPU Co-Processor Engine)", "ngl": 99, "env_vars": {"GGML_SYCL": "ON", "GGML_SYCL_TARGET": "NPU"}})
                return profile
            elif "gpu" in sycl_devices:
                profile.update({"backend": "Intel SYCL (Enterprise Data-Center GPU Layer)", "ngl": 99, "threads": 1, "env_vars": {"GGML_SYCL": "ON", "GGML_SYCL_TARGET": "GPU"}})
                return profile
        except Exception:
            pass

    # 6. Core Enterprise & Workstation Processing Engines (NVIDIA CUDA / AMD ROCm HIP / Vulkan iGPU Layer)
    has_cuda, has_rocm, has_vulkan = False, False, False
    try:
        import ctypes
        if sys_platform == "win32":
            if ctypes.windll.kernel32.LoadLibraryW("nvcuda.dll"): has_cuda = True
            if ctypes.windll.kernel32.LoadLibraryW("vulkan-1.dll"): has_vulkan = True
            if os.path.exists(r"C:\Windows\System32\amdocl64.dll"): has_rocm = True
        else:
            if os.path.exists("/usr/local/cuda") or ctypes.CDLL("libnvidia-ml.so.1", errors=None): has_cuda = True
            if os.path.exists("/opt/rocm") or ctypes.CDLL("libamdhip64.so", errors=None): has_rocm = True
            if ctypes.CDLL("libvulkan.so.1", errors=None): has_vulkan = True
    except Exception:
        pass

    # Handle resolution mapping based on speed performance ranking attributes
    if has_cuda:
        # Extends transparently to Multi-GPU Cluster nodes (A100/H100/RTX arrays)
        profile.update({"backend": "NVIDIA High-Density Matrix (CUDA Pipeline Enabled)", "ngl": 99, "threads": 1, "flags": ["--ngl", "99"]})
    elif has_rocm:
        # Instinct MI-Series / High-Performance Radeon Compute Layers
        profile.update({"backend": "AMD ROCm System Architecture Infrastructure (HIP Core Optimization)", "ngl": 99, "threads": 1, "flags": ["--ngl", "99"]})
    elif has_vulkan:
        # Fallback tracking for Integrated Graphic Layers on Laptops or Secondary Compute Processors
        profile.update({"backend": "Vulkan Cross-Vendor Fabric Optimization (Intel/AMD iGPU)", "ngl": 99, "threads": 1, "flags": ["--ngl", "99", "--vulkan"]})
    elif os.path.exists("/etc/OpenCL/vendors") or shutil.which("clinfo"):
        profile.update({"backend": "Generic OpenCL API Engine Interface Layer", "ngl": 99, "flags": ["--clblast"]})
    elif "ZENDNN_ROOT" in os.environ or os.path.exists("/opt/amd/ZenDNN"):
        # High core-count EPYC / Ryzen thread computing matrices
        profile.update({"backend": "AMD ZenDNN High-Performance Core Engine", "ngl": 0, "env_vars": {"GGML_CPU_AOCL": "ON", "ZENDNN_NUM_THREADS": str(multiprocessing.cpu_count())}})

    return profile

if __name__ == "__main__":
    print("\n======= AUTOSCALE HARDWARE MAPPING ANALYSIS =======")
    for k, v in probe_silicon_and_memory().items():
        print(f"🔹 {k.upper()}: {v}")
    print("===================================================\n")
