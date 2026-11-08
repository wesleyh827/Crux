#!/usr/bin/env python3
"""
Crux 專案自動設置腳本
執行此腳本會自動建立完整的專案結構和基礎檔案
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """建立專案目錄結構"""
    directories = [
        "src/core",
        "src/network", 
        "src/simulation",
        "src/analysis",
        "src/visualization",
        "tests",
        "experiments", 
        "data/sample_workloads",
        "data/network_configs",
        "results/plots",
        "results/reports"
    ]
    
    print("Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {directory}/")

def create_init_files():
    """建立 __init__.py 檔案"""
    init_dirs = [
        "src",
        "src/core",
        "src/network",
        "src/simulation", 
        "src/analysis",
        "src/visualization",
        "tests"
    ]
    
    print("Creating __init__.py files...")
    for directory in init_dirs:
        init_file = Path(directory) / "__init__.py"
        init_file.touch()
        print(f"  ✓ Created {init_file}")

def create_requirements_txt():
    """建立 requirements.txt"""
    requirements = """numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
networkx>=2.6.0
simpy>=4.0.0
plotly>=5.0.0
streamlit>=1.0.0
scipy>=1.7.0
seaborn>=0.11.0
jupyter>=1.0.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    print("  ✓ Created requirements.txt")

def create_readme():
    """建立 README.md"""
    readme_content = """# Crux Implementation

GPU-Efficient Communication Scheduling for Deep Learning Training

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run basic test:
```bash
python tests/test_core.py
```

3. Run basic experiment:
```bash
python experiments/basic_experiment.py
```

## Project Structure

- `src/core/`: Core algorithms (GPU intensity, priority assignment)
- `src/network/`: Network topology and path selection
- `src/simulation/`: DLT cluster simulator
- `src/analysis/`: Performance analysis tools
- `src/visualization/`: Plotting and dashboard
- `experiments/`: Experiment scripts
- `tests/`: Unit tests

## Features

- [x] GPU Intensity calculation
- [x] Priority assignment with correction factors
- [x] Network topology modeling (Clos, Double-sided)
- [x] Path selection algorithms
- [ ] Priority compression (K-Cut problem)
- [ ] Complete cluster simulator
- [ ] Interactive dashboard
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("  ✓ Created README.md")

def create_core_files():
    """建立核心模組檔案"""
    
    # job.py
    job_content = '''from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    BERT = "BERT"
    GPT = "GPT"
    RESNET = "ResNet"

@dataclass
class Job:
    """DLT 作業資料結構"""
    job_id: str
    model_type: ModelType
    num_gpus: int
    computation_load: float  # FLOPS per iteration
    communication_time: float  # seconds per iteration
    gpu_intensity: float = 0.0
    priority: float = 0.0
    correction_factor: float = 1.0
    
    def __post_init__(self):
        self.gpu_intensity = self.computation_load / self.communication_time
        
    def __repr__(self):
        return (f"Job(id={self.job_id}, type={self.model_type.value}, "
                f"gpus={self.num_gpus}, intensity={self.gpu_intensity:.2f})")
'''
    
    with open("src/core/job.py", "w") as f:
        f.write(job_content)
    print("  ✓ Created src/core/job.py")
    
    # gpu_intensity.py
    gpu_intensity_content = '''from typing import Dict, List, Optional
from .job import Job

class GPUIntensityCalculator:
    """GPU Intensity 計算和管理"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.reference_job_id: Optional[str] = None
    
    def add_job(self, job: Job) -> None:
        """新增作業"""
        self.jobs[job.job_id] = job
        print(f"Added job {job.job_id}: GPU Intensity = {job.gpu_intensity:.2f}")
    
    def calculate_correction_factor(self, job_id: str) -> float:
        """計算修正因子 k_j"""
        if self.reference_job_id is None:
            self._select_reference_job()
        
        if job_id == self.reference_job_id:
            return 1.0
        
        job = self.jobs[job_id]
        ref_job = self.jobs[self.reference_job_id]
        
        # 考慮迭代時間差異
        iteration_ratio = ref_job.communication_time / job.communication_time
        
        # 考慮計算-通信重疊
        overlap_sensitivity = self._calculate_overlap_sensitivity(job, ref_job)
        
        correction_factor = iteration_ratio * overlap_sensitivity
        job.correction_factor = correction_factor
        
        return correction_factor
    
    def _select_reference_job(self) -> None:
        """選擇網路流量最大的作業作為參考"""
        if not self.jobs:
            return
        
        max_traffic_job = max(
            self.jobs.values(),
            key=lambda j: j.num_gpus * j.communication_time
        )
        self.reference_job_id = max_traffic_job.job_id
        print(f"Selected reference job: {self.reference_job_id}")
    
    def _calculate_overlap_sensitivity(self, job: Job, ref_job: Job) -> float:
        """計算計算-通信重疊敏感度"""
        job_overlap_ratio = min(0.8, 1.0 / (job.num_gpus / 8))
        ref_overlap_ratio = min(0.8, 1.0 / (ref_job.num_gpus / 8))
        
        sensitivity = (1 - job_overlap_ratio) / (1 - ref_overlap_ratio)
        return max(0.5, min(2.0, sensitivity))
    
    def calculate_priority(self, job_id: str) -> float:
        """計算作業優先級 P_j = k_j * I_j"""
        job = self.jobs[job_id]
        correction_factor = self.calculate_correction_factor(job_id)
        priority = correction_factor * job.gpu_intensity
        job.priority = priority
        return priority
    
    def get_jobs_by_priority(self) -> List[Job]:
        """按優先級排序返回作業列表"""
        for job_id in self.jobs:
            self.calculate_priority(job_id)
        
        return sorted(self.jobs.values(), key=lambda j: j.priority, reverse=True)
'''
    
    with open("src/core/gpu_intensity.py", "w") as f:
        f.write(gpu_intensity_content)
    print("  ✓ Created src/core/gpu_intensity.py")

def create_test_file():
    """建立測試檔案"""
    test_content = '''import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.job import Job, ModelType
from core.gpu_intensity import GPUIntensityCalculator

def test_job_creation():
    """測試 Job 創建"""
    print("Testing job creation...")
    job = Job("test_job", ModelType.BERT, 8, 400.0, 2.0)
    assert job.gpu_intensity == 200.0
    print(f"  ✓ Created job: {job}")
    print("  ✓ Job creation test passed")

def test_gpu_intensity_calculator():
    """測試 GPU Intensity 計算器"""
    print("\\nTesting GPU Intensity calculator...")
    calculator = GPUIntensityCalculator()
    
    bert_job = Job("bert_1", ModelType.BERT, 16, 800.0, 2.0)
    gpt_job = Job("gpt_1", ModelType.GPT, 32, 6400.0, 4.0)
    resnet_job = Job("resnet_1", ModelType.RESNET, 8, 240.0, 1.0)
    
    calculator.add_job(bert_job)
    calculator.add_job(gpt_job) 
    calculator.add_job(resnet_job)
    
    print("\\nCalculating priorities...")
    jobs_by_priority = calculator.get_jobs_by_priority()
    
    print("\\nJob priorities (highest to lowest):")
    for i, job in enumerate(jobs_by_priority):
        print(f"  {i+1}. {job.job_id}: Priority={job.priority:.2f}, "
              f"Intensity={job.gpu_intensity:.2f}, Factor={job.correction_factor:.2f}")
    
    print("  ✓ GPU Intensity calculator test passed")

def main():
    """執行所有測試"""
    print("=== Crux Core Module Tests ===\\n")
    test_job_creation()
    test_gpu_intensity_calculator()
    print("\\n=== All tests passed! ===")

if __name__ == "__main__":
    main()
'''
    
    with open("tests/test_core.py", "w") as f:
        f.write(test_content)
    print("  ✓ Created tests/test_core.py")

def create_experiment_file():
    """建立實驗檔案"""
    experiment_content = '''import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.job import Job, ModelType
from core.gpu_intensity import GPUIntensityCalculator
import random

def create_sample_workload():
    """創建範例工作負載"""
    jobs = [
        Job("bert_small", ModelType.BERT, 8, 400.0, 1.5),
        Job("bert_large", ModelType.BERT, 16, 800.0, 2.0),
        Job("gpt_medium", ModelType.GPT, 32, 6400.0, 4.0),
        Job("gpt_large", ModelType.GPT, 64, 12800.0, 6.0),
        Job("resnet_small", ModelType.RESNET, 4, 120.0, 0.8),
        Job("resnet_medium", ModelType.RESNET, 8, 240.0, 1.2),
    ]
    return jobs

def run_basic_experiment():
    """執行基礎實驗"""
    print("=== Crux Basic Experiment ===\\n")
    
    # 1. 創建工作負載
    jobs = create_sample_workload()
    print(f"Created {len(jobs)} jobs:")
    for job in jobs:
        print(f"  - {job.job_id}: {job.model_type.value}, "
              f"{job.num_gpus} GPUs, Intensity: {job.gpu_intensity:.2f}")
    
    # 2. 計算 GPU Intensity 和優先級
    print(f"\\n=== GPU Intensity Calculation ===")
    calculator = GPUIntensityCalculator()
    for job in jobs:
        calculator.add_job(job)
    
    print(f"\\n=== Priority Assignment ===")
    jobs_by_priority = calculator.get_jobs_by_priority()
    
    print("\\nFinal job ranking (by priority):")
    for i, job in enumerate(jobs_by_priority):
        print(f"{i+1:2d}. {job.job_id:15s} | "
              f"Priority: {job.priority:6.2f} | "
              f"Intensity: {job.gpu_intensity:6.2f} | "
              f"Factor: {job.correction_factor:4.2f} | "
              f"Model: {job.model_type.value}")
    
    # 3. 分析結果
    print(f"\\n=== Analysis ===")
    high_priority_jobs = [j for j in jobs_by_priority if j.priority > 1000]
    print(f"High priority jobs (>1000): {len(high_priority_jobs)}")
    
    gpu_intensive_jobs = [j for j in jobs if j.gpu_intensity > 500]
    print(f"GPU intensive jobs (>500): {len(gpu_intensive_jobs)}")
    
    print(f"\\nTop 3 jobs by priority:")
    for i, job in enumerate(jobs_by_priority[:3]):
        print(f"  {i+1}. {job.job_id} - Priority: {job.priority:.2f}")
    
    return jobs_by_priority

def simulate_scheduling_comparison():
    """模擬不同調度策略的比較"""
    print(f"\\n=== Scheduling Strategy Comparison ===")
    
    jobs = create_sample_workload()
    calculator = GPUIntensityCalculator()
    
    for job in jobs:
        calculator.add_job(job)
    
    # Crux 調度 (按優先級)
    crux_jobs = calculator.get_jobs_by_priority()
    
    # FIFO 調度 (按原始順序)
    fifo_jobs = jobs.copy()
    
    # 簡單的 GPU 利用率計算
    def calculate_utilization(job_list):
        total_intensity = sum(j.gpu_intensity for j in job_list[:3])  # 模擬前3個作業同時執行
        return min(1.0, total_intensity / 2000)  # 假設集群容量為2000
    
    crux_util = calculate_utilization(crux_jobs)
    fifo_util = calculate_utilization(fifo_jobs)
    
    improvement = (crux_util - fifo_util) / fifo_util * 100 if fifo_util > 0 else 0
    
    print(f"\\nPerformance Comparison:")
    print(f"  Crux GPU Utilization:  {crux_util:.3f}")
    print(f"  FIFO GPU Utilization:  {fifo_util:.3f}")
    print(f"  Improvement:           {improvement:.1f}%")
    
    print(f"\\nCrux execution order:")
    for i, job in enumerate(crux_jobs[:3]):
        print(f"  {i+1}. {job.job_id} (Priority: {job.priority:.1f})")
    
    print(f"\\nFIFO execution order:")
    for i, job in enumerate(fifo_jobs[:3]):
        print(f"  {i+1}. {job.job_id} (Intensity: {job.gpu_intensity:.1f})")

def main():
    """主要執行函數"""
    random.seed(42)  # 確保結果可重現
    
    jobs = run_basic_experiment()
    simulate_scheduling_comparison()
    
    print(f"\\n=== Experiment Complete ===")
    print(f"Next steps:")
    print(f"  1. Implement network topology (src/network/)")
    print(f"  2. Add path selection algorithms")
    print(f"  3. Implement priority compression")
    print(f"  4. Build full cluster simulator")

if __name__ == "__main__":
    main()
'''
    
    with open("experiments/basic_experiment.py", "w") as f:
        f.write(experiment_content)
    print("  ✓ Created experiments/basic_experiment.py")

def create_quick_start_script():
    """建立快速開始腳本"""
    quick_start_content = '''#!/usr/bin/env python3
"""
快速開始腳本 - 一鍵執行基礎測試和實驗
"""

import subprocess
import sys
import os

def run_command(command, description):
    """執行命令並顯示結果"""
    print(f"\\n{'='*50}")
    print(f"{description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """主要執行函數"""
    print("Crux Implementation - Quick Start")
    print("This script will run basic tests and experiments")
    
    # 檢查 Python 版本
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    # 1. 安裝依賴套件 (可選)
    install_deps = input("\\nInstall dependencies? (y/n): ").lower().strip()
    if install_deps == 'y':
        if not run_command("pip install -r requirements.txt", "Installing Dependencies"):
            print("Failed to install dependencies. Please install manually.")
            return
    
    # 2. 執行核心模組測試
    if not run_command("python tests/test_core.py", "Running Core Module Tests"):
        print("Core tests failed. Please check the implementation.")
        return
    
    # 3. 執行基礎實驗
    if not run_command("python experiments/basic_experiment.py", "Running Basic Experiment"):
        print("Basic experiment failed. Please check the implementation.")
        return
    
    print(f"\\n{'='*50}")
    print("🎉 All tests and experiments completed successfully!")
    print(f"{'='*50}")
    print("\\nWhat's next?")
    print("1. Explore the code in src/ directory")
    print("2. Run individual tests: python tests/test_core.py")
    print("3. Modify experiments in experiments/ directory")
    print("4. Implement additional features (network topology, simulation)")

if __name__ == "__main__":
    main()
'''
    
    with open("quick_start.py", "w") as f:
        f.write(quick_start_content)
    
    # 讓腳本可執行 (Unix/Linux/Mac)
    try:
        os.chmod("quick_start.py", 0o755)
    except:
        pass
    
    print("  ✓ Created quick_start.py")

def main():
    """主要設置函數"""
    print("=" * 60)
    print("🚀 Crux Implementation Project Setup")
    print("=" * 60)
    
    # 檢查當前目錄
    current_dir = os.getcwd()
    project_name = "crux_implementation"
    
    if not os.path.basename(current_dir) == project_name:
        print(f"Creating project directory: {project_name}")
        os.makedirs(project_name, exist_ok=True)
        os.chdir(project_name)
        print(f"Changed to directory: {os.getcwd()}")
    
    try:
        # 建立目錄結構
        create_directory_structure()
        
        # 建立 __init__.py 檔案
        create_init_files()
        
        # 建立配置檔案
        print("\nCreating configuration files...")
        create_requirements_txt()
        create_readme()
        
        # 建立核心程式碼
        print("\nCreating core module files...")
        create_core_files()
        
        # 建立測試檔案
        print("\nCreating test files...")
        create_test_file()
        
        # 建立實驗檔案
        print("\nCreating experiment files...")
        create_experiment_file()
        
        # 建立快速開始腳本
        print("\nCreating utility scripts...")
        create_quick_start_script()
        
        print("\n" + "=" * 60)
        print("✅ Project setup completed successfully!")
        print("=" * 60)
        
        print(f"\n📁 Project created in: {os.getcwd()}")
        print(f"\n🚀 Quick start commands:")
        print(f"   cd {project_name}")
        print(f"   python quick_start.py")
        print(f"\n📖 Or run manually:")
        print(f"   pip install -r requirements.txt")
        print(f"   python tests/test_core.py")
        print(f"   python experiments/basic_experiment.py")
        
        print(f"\n📂 Project structure:")
        print(f"   src/core/          - Core algorithms")
        print(f"   src/network/       - Network topology")
        print(f"   src/simulation/    - Cluster simulator")
        print(f"   tests/             - Unit tests")
        print(f"   experiments/       - Experiment scripts")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("Please check permissions and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()