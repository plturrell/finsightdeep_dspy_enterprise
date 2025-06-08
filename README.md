# DSPy: Programming—not prompting—Foundation Models

[![PyPI Downloads](https://static.pepy.tech/badge/dspy/month)](https://pepy.tech/projects/dspy)

DSPy is the framework for _programming—rather than prompting—language models_. It allows you to iterate fast on **building modular AI systems** and offers algorithms for **optimizing their prompts and weights**, whether you're building simple classifiers, sophisticated RAG pipelines, or Agent loops.

DSPy stands for Declarative Self-improving Python. Instead of brittle prompts, you write compositional _Python code_ and use DSPy to **teach your LM to deliver high-quality outputs**. Learn more via our [official documentation site](https://dspy.ai/) or meet the community, seek help, or start contributing via this GitHub repo and our [Discord server](https://discord.gg/XCGy2WDCQB).

## Documentation: [dspy.ai](https://dspy.ai)

**Please go to the [DSPy Docs at dspy.ai](https://dspy.ai)**

## Key Features

- **Programmatic Control**: Write modular AI systems in Python with LMs as subroutines
- **Self-Improvement**: Automatically optimize prompts and weights for high-quality outputs
- **GPU Optimized**: Specially optimized for NVIDIA T4 GPUs with auto-tuning capabilities
- **FastAI Integration**: Built-in support for FastAI's training and modeling capabilities
- **Modern Web Interface**: Includes a sleek dashboard for model monitoring and management

## Installation

```bash
pip install dspy
```

To install the very latest from `main`:

```bash
pip install git+https://github.com/stanfordnlp/dspy.git
```

For the full package with all features:

```bash
pip install "dspy[dev,fastai,frontend]"
```

## Backend & Frontend

DSPy now includes powerful backend and frontend components:

### FastAI Backend

The FastAI backend provides seamless integration with FastAI's capabilities:

```python
import dspy
from dspy import FastAIProvider, TextClassificationJob

# Initialize FastAI provider
provider = FastAIProvider()

# Create a text classification training job
job = TextClassificationJob(provider=provider, batch_size=16)

# Fine-tune a model
model_path = provider.finetune(
    job=job,
    model="fastai/text_classifier",
    train_data=(texts, labels),
    train_data_format="list",
    train_kwargs={"epochs": 4, "lr": 2e-5}
)

# Use the fine-tuned model
classifier = provider.load(model_path)
```

### Web Frontend

DSPy now includes a modern web dashboard for monitoring and managing your models:

```python
from dspy import frontend

# Start the frontend server
frontend.start_server(host="127.0.0.1", port=8080)
```

Or via command line:

```bash
python -m dspy.frontend.cli --port 8080
```

Visit http://127.0.0.1:8080 to access the dashboard.

## Docker Deployment

DSPy provides Docker support for easy deployment and testing:

### Local Development with Docker

```bash
# Start the local development environment
docker-compose -f docker-compose.local.yml up -d

# Test all API endpoints
./scripts/test_api_coverage.sh
```

### SAP HANA Cloud Vector Store Integration

DSPy supports SAP HANA Cloud as a vector database for efficient retrieval:

1. **Set up environment variables** in your `.env` file:

```bash
# SAP HANA Cloud Vector Store Configuration
SAP_HANA_HOST=your-hana-host.hanatrial.ondemand.com
SAP_HANA_PORT=443
SAP_HANA_USER=your-hana-user
SAP_HANA_PASSWORD=your-hana-password
SAP_HANA_DATABASE=your-hana-database
SAP_HANA_SCHEMA=PUBLIC
SAP_HANA_TABLE=VECTOR_STORE
DSPY_VECTOR_STORE=sap_hana
```

2. **Use SAP HANA in your DSPy code**:

```python
import dspy
from dspy.retrieve.sap_hana_rm import SAPHanaRM

# Initialize retrieval module
retriever = SAPHanaRM(
    host=os.environ.get("SAP_HANA_HOST"),
    port=int(os.environ.get("SAP_HANA_PORT", 443)),
    user=os.environ.get("SAP_HANA_USER"),
    password=os.environ.get("SAP_HANA_PASSWORD"),
    schema=os.environ.get("SAP_HANA_SCHEMA", "PUBLIC"),
    table=os.environ.get("SAP_HANA_TABLE", "VECTOR_STORE"),
    k=5  # Number of results to retrieve
)

# Use in a RAG pipeline
class RAG(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = retriever
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question)
        return self.generate(context=context, question=question)
```

3. **Test the SAP HANA integration** locally:

```bash
# Test the connection to SAP HANA
python scripts/test_sap_hana.py

# Run the API with mock SAP HANA support
python scripts/local_api_test.py

# Test all endpoints, including vector store endpoints
./scripts/local_endpoint_test.sh
```

### NVIDIA Blueprint Deployment

DSPy is optimized for deployment on NVIDIA Blueprint:

```bash
# Create a deployment configuration
cp blueprint.yaml.template blueprint.yaml

# Edit the configuration with your values
nano blueprint.yaml

# Deploy to NVIDIA Blueprint
nvidia-blueprint deploy -f blueprint.yaml
```

## 📜 Citation & Reading More

If you're looking to understand the framework, please go to the [DSPy Docs at dspy.ai](https://dspy.ai).

If you're looking to understand the underlying research, this is a set of our papers:

**[Jun'24] [Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs](https://arxiv.org/abs/2406.11695)**       
**[Oct'23] [DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714)**     
[Jul'24] [Fine-Tuning and Prompt Optimization: Two Great Steps that Work Better Together](https://arxiv.org/abs/2407.10930)     
[Jun'24] [Prompts as Auto-Optimized Training Hyperparameters](https://arxiv.org/abs/2406.11706)    
[Feb'24] [Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models](https://arxiv.org/abs/2402.14207)         
[Jan'24] [In-Context Learning for Extreme Multi-Label Classification](https://arxiv.org/abs/2401.12178)       
[Dec'23] [DSPy Assertions: Computational Constraints for Self-Refining Language Model Pipelines](https://arxiv.org/abs/2312.13382)   
[Dec'22] [Demonstrate-Search-Predict: Composing Retrieval & Language Models for Knowledge-Intensive NLP](https://arxiv.org/abs/2212.14024.pdf)

To stay up to date or learn more, follow [@lateinteraction](https://twitter.com/lateinteraction) on Twitter.

The **DSPy** logo is designed by **Chuyi Zhang**.

If you use DSPy or DSP in a research paper, please cite our work as follows:

```
@inproceedings{khattab2024dspy,
  title={DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines},
  author={Khattab, Omar and Singhvi, Arnav and Maheshwari, Paridhi and Zhang, Zhiyuan and Santhanam, Keshav and Vardhamanan, Sri and Haq, Saiful and Sharma, Ashutosh and Joshi, Thomas T. and Moazam, Hanna and Miller, Heather and Zaharia, Matei and Potts, Christopher},
  journal={The Twelfth International Conference on Learning Representations},
  year={2024}
}
@article{khattab2022demonstrate,
  title={Demonstrate-Search-Predict: Composing Retrieval and Language Models for Knowledge-Intensive {NLP}},
  author={Khattab, Omar and Santhanam, Keshav and Li, Xiang Lisa and Hall, David and Liang, Percy and Potts, Christopher and Zaharia, Matei},
  journal={arXiv preprint arXiv:2212.14024},
  year={2022}
}
```