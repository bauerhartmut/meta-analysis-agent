import json, sys
sys.stdout.reconfigure(encoding='utf-8')

nb = {
    'metadata': {
        'kaggle': {
            'accelerator': 'gpu',
            'dataSources': [],
            'isGpuEnabled': True,
            'isInternetEnabled': True,
            'language': 'python'
        },
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'}
    },
    'nbformat': 4,
    'nbformat_minor': 5,
    'cells': []
}

def md(text):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': [text]}

def code(text):
    return {'cell_type': 'code', 'metadata': {}, 'source': [text], 'execution_count': None, 'outputs': []}

nb['cells'] = [
    md('# Research Agent QLoRA Fine-Tuning\nFine-tuning Qwen3-1.5B with QLoRA on Kaggle GPU (T4/P100, 16GB).\n\n**Steps:**\n1. Runtime -> Change runtime type -> **GPU T4 x2**\n2. Settings -> Internet -> **ON**\n3. Add Data -> Search `bauerhartmut/research-agent-finetune` -> Add\n4. Run All Cells'),
    md('## 1. Environment Check'),
    code('import os, sys\nprint(f"Python: {sys.version}")\n\nimport torch\nprint(f"PyTorch: {torch.__version__}")\nprint(f"CUDA available: {torch.cuda.is_available()}")\nif torch.cuda.is_available():\n    gpu = torch.cuda.get_device_name(0)\n    vram = torch.cuda.get_device_properties(0).total_mem / 1024**3\n    print(f"GPU: {gpu} ({vram:.1f} GB)")\nelse:\n    print("ERROR: No GPU! Go to Runtime -> Change runtime type -> GPU")\n    print("Without GPU this notebook cannot run.")\n\nimport urllib.request\ntry:\n    urllib.request.urlopen("https://huggingface.co", timeout=5)\n    print("Internet: OK")\nexcept Exception as e:\n    print(f"Internet: FAILED ({e})")\n    print("Model download will not work without internet.")\n\nfor pkg in ["torch", "transformers", "datasets", "accelerate", "peft"]:\n    try:\n        mod = __import__(pkg)\n        ver = getattr(mod, "__version__", "?")\n        print(f"{pkg}: {ver}")\n    except ImportError:\n        print(f"{pkg}: NOT INSTALLED")'),
    md('## 2. Install Missing Packages'),
    code('import subprocess, sys\npkgs = []\ntry:\n    import peft\nexcept ImportError:\n    pkgs.append("peft")\ntry:\n    import bitsandbytes\nexcept ImportError:\n    pkgs.append("bitsandbytes")\ntry:\n    import trl\nexcept ImportError:\n    pkgs.append("trl")\nif pkgs:\n    print(f"Installing: {pkgs}")\n    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + pkgs)\n    print("Done!")\nelse:\n    print("All packages already installed.")\nimport peft, bitsandbytes\nprint(f"peft: {peft.__version__}")\nprint(f"bitsandbytes: {bitsandbytes.__version__}")'),
    md('## 3. Configuration'),
    code('import os\nDATA_SLUG = "bauerhartmut/research-agent-finetune"\nMODEL_NAME = "Qwen/Qwen3-1.5B"\nNUM_EPOCHS = 3\nLEARNING_RATE = 2e-4\nLORA_R = 16\nLORA_ALPHA = 32\nBATCH_SIZE = 4\nGRADIENT_ACCUMULATION = 4\nMAX_SEQ_LENGTH = 1024\nOUTPUT_DIR = "/kaggle/working/qwen3_qlora_output"\nos.makedirs(OUTPUT_DIR, exist_ok=True)\nprint(f"Config: model={MODEL_NAME}, epochs={NUM_EPOCHS}, lr={LEARNING_RATE}")\nprint(f"LoRA: r={LORA_R}, alpha={LORA_ALPHA}")\nprint(f"Output: {OUTPUT_DIR}")'),
    md('## 4. Load Dataset'),
    code('import json, os\nDATA_SLUG_SHORT = DATA_SLUG.split("/")[-1]\nsearch_paths = [f"/kaggle/input/{DATA_SLUG_SHORT}", f"/kaggle/input/{DATA_SLUG}"]\ndata_file = None\nfor path in search_paths:\n    if os.path.exists(path):\n        print(f"Found: {path}")\n        for f in os.listdir(path):\n            if f.endswith(".jsonl"):\n                data_file = os.path.join(path, f)\n                break\n    if data_file:\n        break\nif not data_file:\n    for root, dirs, files in os.walk("/kaggle/input"):\n        for f in files:\n            if f.endswith(".jsonl"):\n                data_file = os.path.join(root, f)\n                break\n        if data_file:\n            break\nif not data_file:\n    print("Available in /kaggle/input:")\n    if os.path.exists("/kaggle/input"):\n        for item in os.listdir("/kaggle/input"):\n            print(f"  {item}")\n    raise FileNotFoundError("No JSONL found! Add dataset as Input Data.")\nprint(f"Loading: {data_file}")\nrecords = [json.loads(l) for l in open(data_file) if l.strip()]\nprint(f"Loaded: {len(records)} records")\nif records:\n    print(f"Sample keys: {list(records[0].keys())}")'),
    md('## 5. Load Model with QLoRA'),
    code('import time, torch\nfrom transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig\nfrom peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training\n\nbnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)\n\ndef load_with_retry(load_fn, name, max_retries=5, delay=30):\n    for attempt in range(max_retries):\n        try:\n            result = load_fn()\n            print(f"Loaded {name} successfully")\n            return result\n        except Exception as e:\n            print(f"Attempt {attempt+1}/{max_retries} failed: {type(e).__name__}: {e}")\n            if attempt < max_retries - 1:\n                print(f"Retrying in {delay}s...")\n                time.sleep(delay)\n            else:\n                raise\n\nprint(f"Loading tokenizer: {MODEL_NAME}")\ntokenizer = load_with_retry(lambda: AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True, padding_side="right"), "tokenizer")\nif tokenizer.pad_token is None:\n    tokenizer.pad_token = tokenizer.eos_token\n\nprint(f"Loading model: {MODEL_NAME}")\ndef load_model():\n    return AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=bnb_config, device_map="auto", trust_remote_code=True, torch_dtype=torch.bfloat16)\n\nmodel = load_with_retry(load_model, "model")\nmodel = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)\n\nlora_config = LoraConfig(r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0.05, target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"], bias="none", task_type="CAUSAL_LM")\nmodel = get_peft_model(model, lora_config)\nmodel.print_trainable_parameters()'),
    md('## 6. Prepare Dataset'),
    code('from datasets import Dataset\n\ndef format_chat(messages, tok):\n    try:\n        return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)\n    except Exception:\n        parts = []\n        for msg in messages:\n            role = msg.get("role", "user")\n            content = msg.get("content", "")\n            parts.append(role.capitalize() + ": " + content)\n        return chr(10).join(parts)\n\nformatted = [{"text": format_chat(r["messages"], tokenizer)} for r in records if "messages" in r]\ndataset = Dataset.from_list(formatted)\ndataset = dataset.train_test_split(test_size=0.05, seed=42)\nprint(f"Train: {len(dataset[chr(39)+chr(116)+chr(114)+chr(97)+chr(105)+chr(110)+chr(39)])}, Val: {len(dataset[chr(39)+chr(116)+chr(101)+chr(115)+chr(116)+chr(39)])}")\nprint(f"Sample text length: {len(formatted[0][chr(39)+chr(116)+chr(101)+chr(120)+chr(116)+chr(39)])} chars")'),
]

print('Half done - continuing...')
