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

def md(t):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': [t]}

def co(t):
    return {'cell_type': 'code', 'metadata': {}, 'source': [t], 'execution_count': None, 'outputs': []}

C = []
C.append(md('# Research Agent QLoRA Fine-Tuning\nFine-tuning Qwen3-1.5B with QLoRA on Kaggle GPU (T4/P100, 16GB).\n\n**Steps:**\n1. Runtime -> Change runtime type -> **GPU T4 x2**\n2. Settings -> Internet -> **ON**\n3. Add Data -> Search `bauerhartmut/research-agent-finetune` -> Add\n4. Run All Cells'))
C.append(md('## 1. Environment Check'))
C.append(co('import os, sys\nprint(f"Python: {sys.version}")\nimport torch\nprint(f"PyTorch: {torch.__version__}")\nprint(f"CUDA available: {torch.cuda.is_available()}")\nif torch.cuda.is_available():\n    gpu = torch.cuda.get_device_name(0)\n    vram = torch.cuda.get_device_properties(0).total_mem / 1024**3\n    print(f"GPU: {gpu} ({vram:.1f} GB)")\nelse:\n    print("ERROR: No GPU! Go to Runtime -> Change runtime type -> GPU")\nimport urllib.request\ntry:\n    urllib.request.urlopen("https://huggingface.co", timeout=5)\n    print("Internet: OK")\nexcept Exception as e:\n    print(f"Internet: FAILED ({e})")\nfor pkg in ["torch", "transformers", "datasets", "accelerate", "peft"]:\n    try:\n        mod = __import__(pkg)\n        print(f"{pkg}: {getattr(mod, chr(95)+chr(95)+chr(118)+chr(101)+chr(114)+chr(115)+chr(105)+chr(111)+chr(110)+chr(95)+chr(95), chr(63))}")\n    except ImportError:\n        print(f"{pkg}: NOT INSTALLED")'))
C.append(md('## 2. Install Missing Packages'))
C.append(co('import subprocess, sys\npkgs = []\nfor pkg_name, imp_name in [("peft","peft"),("bitsandbytes","bitsandbytes"),("trl","trl")]:\n    try:\n        __import__(imp_name)\n    except ImportError:\n        pkgs.append(pkg_name)\nif pkgs:\n    print(f"Installing: {pkgs}")\n    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + pkgs)\n    print("Done!")\nelse:\n    print("All packages already installed.")'))
C.append(md('## 3. Configuration'))
C.append(co('import os\nDATA_SLUG = "bauerhartmut/research-agent-finetune"\nMODEL_NAME = "Qwen/Qwen3-1.5B"\nNUM_EPOCHS = 3\nLEARNING_RATE = 2e-4\nLORA_R = 16\nLORA_ALPHA = 32\nBATCH_SIZE = 4\nGRADIENT_ACCUMULATION = 4\nMAX_SEQ_LENGTH = 1024\nOUTPUT_DIR = "/kaggle/working/qwen3_qlora_output"\nos.makedirs(OUTPUT_DIR, exist_ok=True)\nprint(f"Config: model={MODEL_NAME}, epochs={NUM_EPOCHS}, lr={LEARNING_RATE}")\nprint(f"LoRA: r={LORA_R}, alpha={LORA_ALPHA}")'))
C.append(md('## 4. Load Dataset'))
C.append(co('import json, os\nslug_short = DATA_SLUG.split("/")[-1]\nfound = None\nfor p in [f"/kaggle/input/{slug_short}", f"/kaggle/input/{DATA_SLUG}"]:\n    if os.path.exists(p):\n        for f in os.listdir(p):\n            if f.endswith(".jsonl"):\n                found = os.path.join(p, f)\n                break\n    if found: break\nif not found:\n    for r, ds, fs in os.walk("/kaggle/input"):\n        for f in fs:\n            if f.endswith(".jsonl"):\n                found = os.path.join(r, f)\n                break\n        if found: break\nif not found:\n    print("Available:", os.listdir("/kaggle/input") if os.path.exists("/kaggle/input") else [])\n    raise FileNotFoundError("No JSONL found! Add dataset as Input Data.")\nprint(f"Loading: {found}")\nrecords = [json.loads(l) for l in open(found) if l.strip()]\nprint(f"Loaded: {len(records)} records")\nif records: print(f"Keys: {list(records[0].keys())}")'))
C.append(md('## 5. Load Model with QLoRA'))
C.append(co('import time, torch\nfrom transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig\nfrom peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training\n\nbnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)\n\ndef load_retry(fn, name, retries=5, delay=30):\n    for i in range(retries):\n        try:\n            r = fn()\n            print(f"Loaded {name}")\n            return r\n        except Exception as e:\n            print(f"Attempt {i+1}/{retries} failed: {type(e).__name__}: {e}")\n            if i < retries - 1: time.sleep(delay)\n            else: raise\n\ntokenizer = load_retry(lambda: AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True, padding_side="right"), "tokenizer")\nif tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token\n\ndef load_model():\n    return AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=bnb_config, device_map="auto", trust_remote_code=True, torch_dtype=torch.bfloat16)\n\nmodel = load_retry(load_model, "model")\nmodel = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)\nlora_config = LoraConfig(r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=0.05, target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"], bias="none", task_type="CAUSAL_LM")\nmodel = get_peft_model(model, lora_config)\nmodel.print_trainable_parameters()'))
C.append(md('## 6. Prepare Dataset'))
C.append(co('from datasets import Dataset\n\ndef fmt_chat(msgs, tok):\n    try:\n        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)\n    except:\n        return "\n".join(m.get("role","user").capitalize() + ": " + m.get("content","") for m in msgs)\n\nformatted = [{"text": fmt_chat(r["messages"], tokenizer)} for r in records if "messages" in r]\ntr = len(formatted)\nvl = int(tr * 0.05) + 1\ndataset = Dataset.from_list(formatted).train_test_split(test_size=min(vl, tr-1), seed=42)\nprint(f"Train: {len(dataset[chr(116)+chr(114)+chr(97)+chr(105)+chr(110)])}, Val: {len(dataset[chr(116)+chr(101)+chr(115)+chr(116)])}")\nprint(f"Sample length: {len(formatted[0][chr(116)+chr(101)+chr(120)+chr(116)])} chars")'))
C.append(md('## 7. Train'))
C.append(co('from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling\n\nargs = TrainingArguments(output_dir=OUTPUT_DIR, num_train_epochs=NUM_EPOCHS, per_device_train_batch_size=BATCH_SIZE, gradient_accumulation_steps=GRADIENT_ACCUMULATION, learning_rate=LEARNING_RATE, warmup_ratio=0.1, weight_decay=0.01, logging_steps=1, save_steps=50, save_total_limit=3, bf16=True, gradient_checkpointing=True, optim="paged_adamw_8bit", lr_scheduler_type="cosine", report_to="none", max_grad_norm=0.3, remove_unused_columns=False, eval_strategy="steps", eval_steps=50)\n\ndef tok_fn(x):\n    return tokenizer(x["text"], truncation=True, max_length=MAX_SEQ_LENGTH, padding="max_length")\n\ntr_ds = dataset["train"].map(tok_fn, batched=True, remove_columns=["text"])\nvl_ds = dataset["test"].map(tok_fn, batched=True, remove_columns=["text"])\n\ntrainer = Trainer(model=model, train_dataset=tr_ds, eval_dataset=vl_ds, tokenizer=tokenizer, data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False), args=args)\n\nprint("Starting QLoRA training...")\ntrainer.train()\nprint("Training complete!")'))
C.append(md('## 8. Save Model'))
C.append(co('final_path = f"{OUTPUT_DIR}/final"\ntrainer.save_model(final_path)\ntokenizer.save_pretrained(final_path)\nprint(f"LoRA adapters saved: {final_path}")\n\nprint("Merging LoRA weights...")\nmerged_path = f"{OUTPUT_DIR}/merged"\nmerged_model = model.merge_and_unload()\nmerged_model.save_pretrained(merged_path)\ntokenizer.save_pretrained(merged_path)\nprint(f"Merged model saved: {merged_path}")\n\nimport os\nfor r, ds, fs in os.walk(OUTPUT_DIR):\n    for f in fs:\n        fp = os.path.join(r, f)\n        print(f"  {fp} ({os.path.getsize(fp)/1024:.1f} KB)")'))
C.append(md('## 9. Test Model'))
C.append(co('from transformers import 
