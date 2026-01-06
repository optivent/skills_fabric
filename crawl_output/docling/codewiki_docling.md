# Docling CodeWiki

Generated: 2026-01-06T01:29:16.731661

Repository: https://github.com/docling-project/docling

---

# Docling Overview

<p align="center">
  <a href="https://github.com/docling-project/docling">
    <img loading="lazy" alt="Docling" src="https://github.com/docling-project/docling/raw/main/docs/assets/docling_processing.png" width="100%"/>
  </a>
</p>

# Docling

<p align="center">
  <a href="https://trendshift.io/repositories/12132" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12132" alt="DS4SD%2Fdocling | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

[![arXiv](https://img.shields.io/badge/arXiv-2408.09869-b31b1b.svg)](https://arxiv.org/abs/2408.09869)
[![Docs](https://img.shields.io/badge/docs-live-brightgreen)](https://docling-project.github.io/docling/)
[![PyPI version](https://img.shields.io/pypi/v/docling)](https://pypi.org/project/docling/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docling)](https://pypi.org/project/docling/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License MIT](https://img.shields.io/github/license/docling-project/docling)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/badge/docling/month)](https://pepy.tech/projects/docling)
[![Docling Actor](https://apify.com/actor-badge?actor=vancura/docling?fpr=docling)](https://apify.com/vancura/docling)
[![Chat with Dosu](https://dosu.dev/dosu-chat-badge.svg)](https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask?utm_source=github)
[![Discord](https://img.shields.io/discord/1399788921306746971?color=6A7EC2&logo=discord&logoColor=ffffff)](https://docling.ai/discord)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10101/badge)](https://www.bestpractices.dev/projects/10101)
[![LF AI & Data](https://img.shields.io/badge/LF%20AI%20%26%20Data-003778?logo=linuxfoundation&logoColor=fff&color=0094ff&labelColor=003778)](https://lfaidata.foundation/projects/)

Docling simplifies document processing, parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the gen AI ecosystem.

## Features

* 🗂️ Parsing of [multiple document formats][supported_formats] incl. PDF, DOCX, PPTX, XLSX, HTML, WAV, MP3, VTT, images (PNG, TIFF, JPEG, ...), and more
* 📑 Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, image classification, and more
* 🧬 Unified, expressive [DoclingDocument][docling_document] representation format
* ↪️ Various [export formats][supported_formats] and options, including Markdown, HTML, [DocTags](https://arxiv.org/abs/2503.11576) and lossless JSON
* 🔒 Local execution capabilities for sensitive data and air-gapped environments
* 🤖 Plug-and-play [integrations][integrations] incl. LangChain, LlamaIndex, Crew AI & Haystack for agentic AI
* 🔍 Extensive OCR support for scanned PDFs and images
* 👓 Support of several Visual Language Models ([GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M))
* 🎙️ Audio support with Automatic Speech Recognition (ASR) models
* 🔌 Connect to any agent using the [MCP server](https://docling-project.github.io/docling/usage/mcp/)
* 💻 Simple and convenient CLI

### What's new
* 📤 Structured [information extraction][extraction] \[🧪 beta\]
* 📑 New layout model (**Heron**) by default, for faster PDF parsing
* 🔌 [MCP server](https://docling-project.github.io/docling/usage/mcp/) for agentic applications
* 💬 Parsing of Web Video Text Tracks (WebVTT) files

### Coming soon

* 📝 Metadata extraction, including title, authors, references & language
* 📝 Chart understanding (Barchart, Piechart, LinePlot, etc)
* 📝 Complex chemistry understanding (Molecular structures)

## Installation

To use Docling, simply install `docling` from your package manager, e.g. pip:
```bash
pip install docling
```

Works on macOS, Linux and Windows environments. Both x86_64 and arm64 architectures.

More [detailed installation instructions](https://docling-project.github.io/docling/installation/) are available in the docs.

## Getting started

To convert individual documents with python, use `convert()`, for example:

```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"
```

More [advanced usage options](https://docling-project.github.io/docling/usage/advanced_options/) are available in
the docs.

## CLI

Docling has a built-in CLI to run conversions.

```bash
docling https://arxiv.org/pdf/2206.01062
```

You can also use 🥚[GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M) and other VLMs via Docling CLI:
```bash
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
```
This will use MLX acceleration on supported Apple Silicon hardware.

Read more [here](https://docling-project.github.io/docling/usage/)

## Documentation

Check out Docling's [documentation](https://docling-project.github.io/docling/), for details on
installation, usage, concepts, recipes, extensions, and more.

## Examples

Go hands-on with our [examples](https://docling-project.github.io/docling/examples/),
demonstrating how to address different application use cases with Docling.

## Integrations

To further accelerate your AI application development, check out Docling's native
[integrations](https://docling-project.github.io/docling/integrations/) with popular frameworks
and tools.

## Get help and support

Please feel free to connect with us using the [discussion section](https://github.com/docling-project/docling/discussions).

## Technical report

For more details on Docling's inner workings, check out the [Docling Technical Report](https://arxiv.org/abs/2408.09869).

## Contributing

Please read [Contributing to Docling](https://github.com/docling-project/docling/blob/main/CONTRIBUTING.md) for details.

## References

If you use Docling in your projects, please consider citing the following:

```bib
@techreport{Docling,
  author = {Deep Search Team},
  month = {8},
  title = {Docling Technical Report},
  url = {https://arxiv.org/abs/2408.09869},
  eprint = {2408.09869},
  doi = {10.48550/arXiv.2408.09869},
  version = {1.0.0},
  year = {2024}
}
```

## License

The Docling codebase is under MIT license.
For individual model usage, please refer to the model licenses found in the original packages.

## LF AI & Data

Docling is hosted as a project in the [LF AI & Data Foundation](https://lfaidata.foundation/projects/).

### IBM ❤️ Open Source AI

The project was started by the AI for knowledge team at IBM Research Zurich.

[supported_formats]: https://docling-project.github.io/docling/usage/supported_formats/
[docling_document]: https://docling-project.github.io/docling/concepts/docling_document/
[integrations]: https://docling-project.github.io/docling/integrations/
[extraction]: https://docling-project.github.io/docling/examples/extraction/


---

# Index

<p align="center">
  <img loading="lazy" alt="Docling" src="assets/docling_processing.png" width="100%" />
  <a href="https://trendshift.io/repositories/12132" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12132" alt="DS4SD%2Fdocling | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

[![arXiv](https://img.shields.io/badge/arXiv-2408.09869-b31b1b.svg)](https://arxiv.org/abs/2408.09869)
[![PyPI version](https://img.shields.io/pypi/v/docling)](https://pypi.org/project/docling/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docling)](https://pypi.org/project/docling/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License MIT](https://img.shields.io/github/license/docling-project/docling)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/badge/docling/month)](https://pepy.tech/projects/docling)
[![Docling Actor](https://apify.com/actor-badge?actor=vancura/docling?fpr=docling)](https://apify.com/vancura/docling)
[![Chat with Dosu](https://dosu.dev/dosu-chat-badge.svg)](https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask?utm_source=github)
[![Discord](https://img.shields.io/discord/1399788921306746971?color=6A7EC2&logo=discord&logoColor=ffffff)](https://docling.ai/discord)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10101/badge)](https://www.bestpractices.dev/projects/10101)
[![LF AI & Data](https://img.shields.io/badge/LF%20AI%20%26%20Data-003778?logo=linuxfoundation&logoColor=fff&color=0094ff&labelColor=003778)](https://lfaidata.foundation/projects/)

Docling simplifies document processing, parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the gen AI ecosystem.

## Getting started

🐣 Ready to kick off your Docling journey? Let's dive right into it!

<div class="grid">
  <a href="../docling/getting_started/installation/" class="card"><b>⬇️ Installation</b><br />Quickly install Docling in your environment</a>
  <a href="../docling/getting_started/quickstart/" class="card"><b>▶️ Quickstart</b><br />Get a jumpstart on basic Docling usage</a>
  <a href="../docling/concepts/" class="card"><b>🧩 Concepts</b><br />Learn Docling fundamentals and get a glimpse under the hood</a>
  <a href="../docling/examples/" class="card"><b>🧑🏽‍🍳 Examples</b><br />Try out recipes for various use cases, including conversion, RAG, and more</a>
  <a href="../docling/integrations/" class="card"><b>🤖 Integrations</b><br />Check out integrations with popular AI tools and frameworks</a>
  <a href="../docling/reference/document_converter/" class="card"><b>📖 Reference</b><br />See more API details</a>
</div>

## Features

* 🗂️  Parsing of [multiple document formats][supported_formats] incl. PDF, DOCX, PPTX, XLSX, HTML, WAV, MP3, VTT, images (PNG, TIFF, JPEG, ...), and more
* 📑 Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, image classification, and more
* 🧬 Unified, expressive [DoclingDocument][docling_document] representation format
* ↪️  Various [export formats][supported_formats] and options, including Markdown, HTML, [DocTags](https://arxiv.org/abs/2503.11576) and lossless JSON
* 🔒 Local execution capabilities for sensitive data and air-gapped environments
* 🤖 Plug-and-play [integrations][integrations] incl. LangChain, LlamaIndex, Crew AI & Haystack for agentic AI
* 🔍 Extensive OCR support for scanned PDFs and images
* 👓 Support of several Visual Language Models ([GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M))
* 🎙️  Support for Audio with Automatic Speech Recognition (ASR) models
* 🔌 Connect to any agent using the [Docling MCP](https://docling-project.github.io/docling/usage/mcp/) server
* 💻 Simple and convenient CLI

### What's new
* 📤 Structured [information extraction][extraction] \[🧪 beta\]
* 📑 New layout model (**Heron**) by default, for faster PDF parsing
* 🔌 [MCP server](https://docling-project.github.io/docling/usage/mcp/) for agentic applications
* 💬 Parsing of Web Video Text Tracks (WebVTT) files

### Coming soon

* 📝 Metadata extraction, including title, authors, references & language
* 📝 Chart understanding (Barchart, Piechart, LinePlot, etc)
* 📝 Complex chemistry understanding (Molecular structures)

## What's next

🚀 The journey has just begun! Join us and become a part of the growing Docling community.

- <a href="https://github.com/docling-project/docling">:fontawesome-brands-github: GitHub</a>
- <a href="https://docling.ai/discord">:fontawesome-brands-discord: Discord</a>
- <a href="https://linkedin.com/company/docling/">:fontawesome-brands-linkedin: LinkedIn</a>

## Live assistant

Do you want to leverage the power of AI and get live support on Docling?
Try out the [Chat with Dosu](https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask?utm_source=github) functionalities provided by our friends at [Dosu](https://dosu.dev/).

[![Chat with Dosu](https://dosu.dev/dosu-chat-badge.svg)](https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask?utm_source=github)

## LF AI & Data

Docling is hosted as a project in the [LF AI & Data Foundation](https://lfaidata.foundation/projects/).

### IBM ❤️ Open Source AI

The project was started by the AI for knowledge team at IBM Research Zurich.

[supported_formats]: ./usage/supported_formats.md
[docling_document]: ./concepts/docling_document.md
[integrations]: ./integrations/index.md


---

# Convert a single file to Markdown (default)

## What's new

Docling v2 introduces several new features:

- Understands and converts PDF, MS Word, MS Powerpoint, HTML and several image formats
- Produces a new, universal document representation which can encapsulate document hierarchy
- Comes with a fresh new API and CLI

## Changes in Docling v2

### CLI

We updated the command line syntax of Docling v2 to support many formats. Examples are seen below.
```shell
# Convert a single file to Markdown (default)
docling myfile.pdf

# Convert a single file to Markdown and JSON, without OCR
docling myfile.pdf --to json --to md --no-ocr

# Convert PDF files in input directory to Markdown (default)
docling ./input/dir --from pdf

# Convert PDF and Word files in input directory to Markdown and JSON
docling ./input/dir --from pdf --from docx --to md --to json --output ./scratch

# Convert all supported files in input directory to Markdown, but abort on first error
docling ./input/dir --output ./scratch --abort-on-error

```

**Notable changes from Docling v1:**

- The standalone switches for different export formats are removed, and replaced with `--from` and `--to` arguments, to define input and output formats respectively.
- The new `--abort-on-error` will abort any batch conversion as soon an error is encountered
- The `--backend` option for PDFs was removed

### Setting up a [`DocumentConverter`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L178)

To accommodate many input formats, we changed the way you need to set up your [`DocumentConverter`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L178) object.
You can now define a list of allowed formats on the [`DocumentConverter`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L178) initialization, and specify custom options
per-format if desired. By default, all supported formats are allowed. If you don't provide `format_options`, defaults
will be used for all `allowed_formats`.

Format options can include the pipeline class to use, the options to provide to the pipeline, and the document backend.
They are provided as format-specific types, such as [`PdfFormatOption`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L137) or [`WordFormatOption`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L95), as seen below.

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

## Default initialization still works as before:
# doc_converter = DocumentConverter()


# previous [`PipelineOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L301) is now [`PdfPipelineOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L401)
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = True
#...

## Custom options are now defined per format.
doc_converter = (
    DocumentConverter(  # all of the below is optional, has internal defaults.
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.IMAGE,
            InputFormat.DOCX,
            InputFormat.HTML,
            InputFormat.PPTX,
        ],  # whitelist formats, non-matching files are ignored.
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, # pipeline options go here.
                backend=PyPdfiumDocumentBackend # optional: pick an alternative backend
            ),
            InputFormat.DOCX: WordFormatOption(
                pipeline_cls=SimplePipeline # default for office formats and HTML
            ),
        },
    )
)
```

**Note**: If you work only with defaults, all remains the same as in Docling v1.

More options are shown in the following example units:

- [run_with_formats.py](examples/run_with_formats.py)
- [custom_convert.py](examples/custom_convert.py)

### Converting documents

We have simplified the way you can feed input to the [`DocumentConverter`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L178) and renamed the conversion methods for
better semantics. You can now call the conversion directly with a single file, or a list of input files,
or `DocumentStream` objects, without constructing a `DocumentConversionInput` object first.

* [`DocumentConverter.convert`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L284) now converts a single file input (previously `DocumentConverter.convert_single`).
* [`DocumentConverter.convert_all`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L328) now converts many files at once (previously [`DocumentConverter.convert`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L284)).


```python
...
from docling.datamodel.document import ConversionResult
## Convert a single file (from URL or local path)
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Convert several files at once:

input_files = [
    "tests/data/html/wiki_duck.html",
    "tests/data/docx/word_sample.docx",
    "tests/data/docx/lorem_ipsum.docx",
    "tests/data/pptx/powerpoint_sample.pptx",
    "tests/data/2305.03393v1-pg9-img.png",
    "tests/data/pdf/2206.01062.pdf",
]

# Directly pass list of files or streams to `convert_all`
conv_results_iter = doc_converter.convert_all(input_files) # previously `convert`

```
Through the `raises_on_error` argument, you can also control if the conversion should raise exceptions when first
encountering a problem, or resiliently convert all files first and reflect errors in each file's conversion status.
By default, any error is immediately raised and the conversion aborts (previously, exceptions were swallowed).

```python
...
conv_results_iter = doc_converter.convert_all(input_files, raises_on_error=False) # previously `convert`

```

### Access document structures

We have simplified how you can access and export the converted document data, too. Our universal document representation
is now available in conversion results as a `DoclingDocument` object.
`DoclingDocument` provides a neat set of APIs to construct, iterate and export content in the document, as shown below.

```python
import pandas as pd
from docling_core.types.doc import TextItem, TableItem

conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Inspect the converted document:
conv_result.document.print_element_tree()

## Iterate the elements in reading order, including hierarchy level:
for item, level in conv_result.document.iterate_items():
    if isinstance(item, TextItem):
        print(item.text)
    elif isinstance(item, TableItem):
        table_df: pd.DataFrame = item.export_to_dataframe(doc=conv_result.document)
        print(table_df.to_markdown())
    elif ...:
        #...
```

**Note**: While it is deprecated, you can _still_ work with the Docling v1 document representation, it is available as:
```shell
conv_result.legacy_document # provides the representation in previous ExportedCCSDocument type
```

### Export into JSON, Markdown, Doctags
**Note**: All `render_...` methods in [`ConversionResult`](https://github.com/docling-project/docling/blob/main/docling/datamodel/document.py#L417) have been removed in Docling v2,
and are now available on `DoclingDocument` as:

- `DoclingDocument.export_to_dict`
- `DoclingDocument.export_to_markdown`
- `DoclingDocument.export_to_document_tokens`

```python
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Export to desired format:
print(json.dumps(conv_res.document.export_to_dict()))
print(conv_res.document.export_to_markdown())
print(conv_res.document.export_to_document_tokens())
```

**Note**: While it is deprecated, you can _still_ export Docling v1 JSON format. This is available through the same
methods as on the `DoclingDocument` type:
```shell
## Export legacy document representation to desired format, for v1 compatibility:
print(json.dumps(conv_res.legacy_document.export_to_dict()))
print(conv_res.legacy_document.export_to_markdown())
print(conv_res.legacy_document.export_to_document_tokens())
```

### Reload a `DoclingDocument` stored as JSON

You can save and reload a `DoclingDocument` to disk in JSON format using the following codes:

```python
# Save to disk:
doc: DoclingDocument = conv_res.document # produced from conversion result...

with Path("./doc.json").open("w") as fp:
    fp.write(json.dumps(doc.export_to_dict())) # use `export_to_dict` to ensure consistency

# Load from disk:
with Path("./doc.json").open("r") as fp:
    doc_dict = json.loads(fp.read())
    doc = DoclingDocument.model_validate(doc_dict) # use standard pydantic API to populate doc

```

### Chunking

Docling v2 defines new base classes for chunking:

- `BaseMeta` for chunk metadata
- `BaseChunk` containing the chunk text and metadata, and
- `BaseChunker` for chunkers, producing chunks out of a `DoclingDocument`.

Additionally, it provides an updated `HierarchicalChunker` implementation, which
leverages the new `DoclingDocument` and provides a new, richer chunk output format, including:

- the respective doc items for grounding
- any applicable headings for context
- any applicable captions for context

For an example, check out [Chunking usage](usage.md#chunking).


---

## Source References

- [`DocumentConverter`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L178) - Convert documents of various input formats to Docling documents.
- [`PdfFormatOption`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L137)
- [`WordFormatOption`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L95)
- [`PipelineOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L301) - Base pipeline options.
- [`PdfPipelineOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L401) - Options for the PDF pipeline.
- [`DocumentConverter.convert`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L284) - Convert one document fetched from a file path, URL, or DocumentStream.
- [`DocumentConverter.convert_all`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L328) - Convert multiple documents from file paths, URLs, or DocumentStreams.
- [`ConversionResult`](https://github.com/docling-project/docling/blob/main/docling/datamodel/document.py#L417)


---

# Haystack

Docling is available as a converter in [Haystack](https://haystack.deepset.ai/):

- 📖 [Docling Haystack integration docs][docs]
- 💻 [Docling Haystack integration GitHub][github]
- 🧑🏽‍🍳 [Docling Haystack integration example][example]
- 📦 [Docling Haystack integration PyPI][pypi]

[github]: https://github.com/docling-project/docling-haystack
[docs]: https://haystack.deepset.ai/integrations/docling
[pypi]: https://pypi.org/project/docling-haystack
[example]: ../examples/rag_haystack.ipynb


---

# Opencontracts

Docling is available an ingestion engine for [OpenContracts](https://github.com/JSv4/OpenContracts), allowing you to use Docling's OCR engine(s), chunker(s), labels, etc. and load them into a platform supporting bulk data extraction, text annotating, and question-answering:

- 💻 [OpenContracts GitHub](https://github.com/JSv4/OpenContracts)
- 📖 [OpenContracts Docs](https://jsv4.github.io/OpenContracts/)
- ▶️ [OpenContracts x Docling PDF annotation screen capture](https://github.com/JSv4/OpenContracts/blob/main/docs/assets/images/gifs/PDF%20Annotation%20Flow.gif)


---

# Index

In this space, you can explore various Docling integrations with leading frameworks and tools!

Here some of our picks to get you started:

- [🦜️🔗 LangChain](./langchain.md)
- [༄ Langflow](./langflow.md)
- [🦙 LlamaIndex](./llamaindex.md)
- [🌾 Haystack](./haystack.md)
- [🇨 Crew AI](./crewai.md)

👈 ... and there is much more: explore all integrations using the navigation menu on the side

<div class="grid" style="text-align: center">
    <div class="card">
        <img loading="lazy" alt="Part of Docling's ecosystem" src="../assets/docling_ecosystem.png" width="75%" />
        <hr />
        A glimpse into Docling's ecosystem
    </div>
</div>


---

# Rhel Ai

Docling is powering document processing in [Red Hat Enterprise Linux AI (RHEL AI)](https://rhel.ai),
enabling users to unlock the knowledge hidden in documents and present it to
InstructLab's fine-tuning for aligning AI models to the user's specific data.

- 📣 [RHEL AI 1.3 announcement](https://www.redhat.com/en/about/press-releases/red-hat-delivers-next-wave-gen-ai-innovation-new-red-hat-enterprise-linux-ai-capabilities)
- ✍️ RHEL blog posts:
    - [RHEL AI 1.3 Docling context aware chunking: What you need to know](https://www.redhat.com/en/blog/rhel-13-docling-context-aware-chunking-what-you-need-know)
    - [Docling: The missing document processing companion for generative AI](https://www.redhat.com/en/blog/docling-missing-document-processing-companion-generative-ai)


---

# Txtai

Docling is available as a text extraction backend for [txtai](https://neuml.github.io/txtai/).

- 💻 [txtai GitHub][github]
- 📖 [txtai docs][docs]
- 📖 [txtai Docling backend][integration_docs]

[github]: https://github.com/neuml/txtai
[docs]: https://neuml.github.io/txtai
[integration_docs]: https://neuml.github.io/txtai/pipeline/data/filetohtml/#docling


---

# Hector

Docling is available in [Hector](https://gohector.dev) as an MCP-based document parser
for RAG systems and document stores.

Hector is a production-grade A2A-native agent platform that integrates with Docling via
the [MCP server](../usage/mcp.md) for advanced document parsing capabilities.

- 💻 [Hector GitHub][github]
- 📖 [Hector Docs][docs]
- 📖 [Using Docling with Hector][tutorial]

[github]: https://github.com/kadirpekel/hector
[docs]: https://gohector.dev
[tutorial]: https://gohector.dev/blog/posts/using-docling-with-hector/


---

# Cloudera

Docling is available in [Cloudera](https://www.cloudera.com/) through the *RAG Studio*
Accelerator for Machine Learning Projects (AMP).

- 💻 [RAG Studio AMP GitHub][github]

[github]: https://github.com/cloudera/CML_AMP_RAG_Studio


---

# Crewai

Docling is available in [CrewAI](https://www.crewai.com/) as the `CrewDoclingSource`
knowledge source.

- 💻 [Crew AI GitHub][github]
- 📖 [Crew AI knowledge docs][docs]
- 📦 [Crew AI PyPI][package]

[github]: https://github.com/crewAIInc/crewAI/
[docs]: https://docs.crewai.com/concepts/knowledge
[package]: https://pypi.org/project/crewai/


---

# Openwebui

Docling is available as a plugin for [Open WebUI](https://github.com/open-webui/open-webui).

- 📖 [Docs][docs]
- 💻 [GitHub][github]

[github]: https://github.com/open-webui/open-webui
[docs]: https://docs.openwebui.com/features/rag/document-extraction/docling


---

# Langchain

Docling is available as an official [LangChain](https://python.langchain.com/) extension.

To get started, check out the [step-by-step guide in LangChain][guide].

- 📖 [LangChain Docling integration docs][docs]
- 💻 [LangChain Docling integration GitHub][github]
- 🧑🏽‍🍳 [LangChain Docling integration example][example]
- 📦 [LangChain Docling integration PyPI][pypi]

[docs]: https://python.langchain.com/docs/integrations/providers/docling/
[github]: https://github.com/docling-project/docling-langchain
[guide]: https://python.langchain.com/docs/integrations/document_loaders/docling/
[example]: ../examples/rag_langchain.ipynb
[pypi]: https://pypi.org/project/langchain-docling/


---

# Nvidia

Docling is powering the NVIDIA *PDF to Podcast* agentic AI blueprint:

- [🏠 PDF to Podcast home](https://build.nvidia.com/nvidia/pdf-to-podcast)
- [💻 PDF to Podcast GitHub](https://github.com/NVIDIA-AI-Blueprints/pdf-to-podcast)
- [📣 PDF to Podcast announcement](https://nvidianews.nvidia.com/news/nvidia-launches-ai-foundation-models-for-rtx-ai-pcs)
- [✍️ PDF to Podcast blog post](https://blogs.nvidia.com/blog/agentic-ai-blueprints/)


---

# Spacy

Docling is available in [spaCy](https://spacy.io/) as the *spaCy Layout* plugin.

More details can be found in this [blog post][blog].

- 💻 [SpacyLayout GitHub][github]
- 📖 [SpacyLayout docs][docs]
- 📦 [SpacyLayout PyPI][pypi]

[github]: https://github.com/explosion/spacy-layout
[docs]: https://github.com/explosion/spacy-layout?tab=readme-ov-file#readme
[pypi]: https://pypi.org/project/spacy-layout/
[blog]: https://explosion.ai/blog/pdfs-nlp-structured-data


---

# Vectara

Docling is available as a document parser in [Vectara](https://www.vectara.com/).

- 💻 [Vectara GitHub org](https://github.com/vectara)
    - [vectara-ingest GitHub repo](https://github.com/vectara/vectara-ingest)
- 📖 [Vectara docs](https://docs.vectara.com/)


---

# Quarkus

Docling is available as a [Quarkus](https://quarkus.io) extension! See the [extension documentation](https://quarkus.io/extensions/io.quarkiverse.docling/quarkus-docling) for more information.

- 📖 [Docs](https://docs.quarkiverse.io/quarkus-docling/dev)
- 💻 [GitHub](https://github.com/quarkiverse/quarkus-docling)


---

# Llamaindex

Docling is available as an official [LlamaIndex](https://docs.llamaindex.ai/) extension.

To get started, check out the [step-by-step guide in LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/data_connectors/DoclingReaderDemo/).

## Components

### Docling Reader

Reads document files and uses Docling to populate LlamaIndex `Document` objects — either serializing Docling's data model (losslessly, e.g. as JSON) or exporting to a simplified format (lossily, e.g. as Markdown).

- 💻 [Docling Reader GitHub](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/readers/llama-index-readers-docling)
- 📖 [Docling Reader docs](https://docs.llamaindex.ai/en/stable/api_reference/readers/docling/)
- 📦 [Docling Reader PyPI](https://pypi.org/project/llama-index-readers-docling/)

### Docling Node Parser

Reads LlamaIndex `Document` objects populated in Docling's format by Docling Reader and, using its knowledge of the Docling format, parses them to LlamaIndex `Node` objects for downstream usage in LlamaIndex applications, e.g. as chunks for embedding.

- 💻 [Docling Node Parser GitHub](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/node_parser/llama-index-node-parser-docling)
- 📖 [Docling Node Parser docs](https://docs.llamaindex.ai/en/stable/api_reference/node_parser/docling/)
- 📦 [Docling Node Parser PyPI](https://pypi.org/project/llama-index-node-parser-docling/)


---

# Kotaemon

Docling is available in [Kotaemon](https://cinnamon.github.io/kotaemon/) as the `DoclingReader` loader:

- 💻 [Kotaemon GitHub][github]
- 📖 [DoclingReader docs][docs]
- ⚙️ [Docling setup in Kotaemon][setup]

[github]: https://github.com/Cinnamon/kotaemon
[docs]: https://cinnamon.github.io/kotaemon/reference/loaders/docling_loader/
[setup]: https://cinnamon.github.io/kotaemon/development/?h=docling#setup-multimodal-document-parsing-ocr-table-parsing-figure-extraction


---

# Apify

You can run Docling in the cloud without installation using the [Docling Actor][apify] on Apify platform. Simply provide a document URL and get the processed result:

<a href="https://apify.com/vancura/docling?fpr=docling"><img src="https://apify.com/ext/run-on-apify.png" alt="Run Docling Actor on Apify" width="176" height="39" /></a>

```bash
apify call vancura/docling -i '{
  "options": {
    "to_formats": ["md", "json", "html", "text", "doctags"]
  },
  "http_sources": [
    {"url": "https://vancura.dev/assets/actor-test/facial-hairstyles-and-filtering-facepiece-respirators.pdf"},
    {"url": "https://arxiv.org/pdf/2408.09869"}
  ]
}'
```

The Actor stores results in:

* Processed document in key-value store (`OUTPUT_RESULT`)
* Processing logs (`DOCLING_LOG`)
* Dataset record with result URL and status

Read more about the [Docling Actor](.actor/README.md), including how to use it via the Apify API and CLI.

- 💻 [GitHub][github]
- 📖 [Docs][docs]
- 📦 [Docling Actor][apify]

[github]: https://github.com/docling-project/docling/tree/main/.actor/
[docs]: https://github.com/docling-project/docling/tree/main/.actor/README.md
[apify]: https://apify.com/vancura/docling?fpr=docling






---

# Instructlab

Docling is powering document processing in [InstructLab][home],
enabling users to unlock the knowledge hidden in documents and present it to
InstructLab's fine-tuning for aligning AI models to the user's specific data.

More details can be found in this [blog post][blog].

- 🏠 [InstructLab home][home]
- 💻 [InstructLab GitHub][github]
- 🧑🏻‍💻 [InstructLab UI][ui]
- 📖 [InstructLab docs][docs]

[home]: https://instructlab.ai
[github]: https://github.com/instructlab
[ui]: https://ui.instructlab.ai/
[docs]: https://docs.instructlab.ai/
[blog]: https://www.redhat.com/en/blog/docling-missing-document-processing-companion-generative-ai


---

# Langflow

Docling is available on the [Langflow](https://www.langflow.org/) visual low-code platform.

- 📖 [Langflow Docling docs][docs]
- ▶️ [Langflow Docling video tutorial][video]
- 💻 [Langflow GitHub][github]

[docs]: https://docs.langflow.org/integrations-docling
[video]: https://www.youtube.com/watch?v=5DuS6uRI5OM
[github]: https://github.com/langflow-ai/langflow/


---

# Bee

Docling is available as an extraction backend in the [Bee][github] framework.

- 💻 [Bee GitHub][github]
- 📖 [Bee docs][docs]
- 📦 [Bee NPM][package]

[github]: https://github.com/i-am-bee
[docs]: https://i-am-bee.github.io/bee-agent-framework/
[package]: https://www.npmjs.com/package/bee-agent-framework


---

# Arconia

Docling is available as a Java integration in [Arconia][github].

- 💻 [GitHub][github]
- 📖 [Docs][docs]
- 🧑🏽‍🍳 [Example][example]

[github]: https://github.com/arconia-io/arconia
[docs]: https://arconia.io/docs/arconia/latest/integrations/docling/
[example]: https://github.com/arconia-io/arconia-examples/tree/main/arconia-docling


---

# Data Prep Kit

Docling is used by the [Data Prep Kit](https://data-prep-kit.github.io/data-prep-kit/) open-source toolkit for preparing unstructured data for LLM application development ranging from laptop scale to datacenter scale.

## Components
### PDF ingestion to Parquet
- 💻 [Docling2Parquet source](https://github.com/data-prep-kit/data-prep-kit/tree/dev/transforms/language/docling2parquet)
- 📖 [Docling2Parquet docs](https://data-prep-kit.github.io/data-prep-kit/transforms/language/pdf2parquet/)

### Document chunking
- 💻 [Doc Chunking source](https://github.com/data-prep-kit/data-prep-kit/tree/dev/transforms/language/doc_chunk)
- 📖 [Doc Chunking docs](https://data-prep-kit.github.io/data-prep-kit/transforms/language/doc_chunk/)


---

# Docetl

Docling is available as a file conversion method in [DocETL](https://github.com/ucbepic/docetl):

- 💻 [DocETL GitHub][github]
- 📖 [DocETL docs][docs]
- 📦 [DocETL PyPI][pypi]

[github]: https://github.com/ucbepic/docetl
[docs]: https://ucbepic.github.io/docetl/
[pypi]: https://pypi.org/project/docetl/


---

# Prodigy

Docling is available in [Prodigy][home] as a [Prodigy-PDF plugin][plugin] recipe.

More details can be found in this [blog post][blog].

- 🌐 [Prodigy home][home]
- 🔌 [Prodigy-PDF plugin][plugin]
- 🧑🏽‍🍳 [pdf-spans.manual recipe][recipe]

[home]: https://prodi.gy/
[plugin]: https://prodi.gy/docs/plugins#pdf
[recipe]: https://prodi.gy/docs/plugins#pdf-spans.manual
[blog]: https://explosion.ai/blog/pdfs-nlp-structured-data


---

# Installation

To use Docling, simply install `docling` from your Python package manager, e.g. pip:
```bash
pip install docling
```

Works on macOS, Linux, and Windows, with support for both x86_64 and arm64 architectures.

??? "Alternative PyTorch distributions"

    The Docling models depend on the [PyTorch](https://pytorch.org/) library.
    Depending on your architecture, you might want to use a different distribution of `torch`.
    For example, you might want support for different accelerator or for a cpu-only version.
    All the different ways for installing `torch` are listed on their website <https://pytorch.org/>.

    One common situation is the installation on Linux systems with cpu-only support.
    In this case, we suggest the installation of Docling with the following options

    ```bash
    # Example for installing on the Linux cpu-only version
    pip install docling --extra-index-url https://download.pytorch.org/whl/cpu
    ```

??? "Installation on macOS Intel (x86_64)"

    When installing Docling on macOS with Intel processors, you might encounter errors with PyTorch compatibility.
    This happens because newer PyTorch versions (2.6.0+) no longer provide wheels for Intel-based Macs.

    If you're using an Intel Mac, install Docling with compatible PyTorch
    **Note:** PyTorch 2.2.2 requires Python 3.12 or lower. Make sure you're not using Python 3.13+.

    ```bash
    # For uv users
    uv add torch==2.2.2 torchvision==0.17.2 docling

    # For pip users
    pip install "docling[mac_intel]"

    # For Poetry users
    poetry add docling
    ```

## Available extras

The `docling` package is designed to offer a working solution for the Docling default options.
Some Docling functionalities require additional third-party packages and are therefore installed only if selected as extras (or installed independently).

The following table summarizes the extras available in the `docling` package. They can be activated with:
`pip install "docling[NAME1,NAME2]"`


| Extra | Description |
| - | - |
| `asr` | Installs dependencies for running the ASR pipeline. |
| `vlm` | Installs dependencies for running the VLM pipeline. |
| `easyocr` | Installs the [EasyOCR](https://github.com/JaidedAI/EasyOCR) OCR engine. |
| `tesserocr` | Installs the Tesseract binding for using it as OCR engine. |
| `ocrmac` | Installs the OcrMac OCR engine. |
| `rapidocr` | Installs the [RapidOCR](https://github.com/RapidAI/RapidOCR) OCR engine with [onnxruntime](https://github.com/microsoft/onnxruntime/) backend. |


### OCR engines


Docling supports multiple OCR engines for processing scanned documents. The current version provides
the following engines.

| Engine | Installation | Usage |
| ------ | ------------ | ----- |
| [EasyOCR](https://github.com/JaidedAI/EasyOCR) | `easyocr` extra or via `pip install easyocr`. | [`EasyOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L163) |
| Tesseract | System dependency. See description for Tesseract and Tesserocr below.  | [`TesseractOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L201) |
| Tesseract CLI | System dependency. See description below. | [`TesseractCliOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L185) |
| OcrMac | System dependency. See description below. | [`OcrMacOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L216) |
| [RapidOCR](https://github.com/RapidAI/RapidOCR) | `rapidocr` extra can or via `pip install rapidocr onnxruntime` | [`RapidOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L119) |
| [OnnxTR](https://github.com/felixdittrich92/OnnxTR) | Can be installed via the plugin system `pip install "docling-ocr-onnxtr[cpu]"`. Please take a look at [docling-OCR-OnnxTR](https://github.com/felixdittrich92/docling-OCR-OnnxTR).| `OnnxtrOcrOptions` |

The Docling [`DocumentConverter`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L178) allows to choose the OCR engine with the `ocr_options` settings. For example

```python
from docling.datamodel.base_models import ConversionStatus, PipelineOptions
from docling.datamodel.pipeline_options import PipelineOptions, EasyOcrOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter

pipeline_options = PipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions()  # Use Tesseract

doc_converter = DocumentConverter(
    pipeline_options=pipeline_options,
)
```

??? "Tesseract installation"

    [Tesseract](https://github.com/tesseract-ocr/tesseract) is a popular OCR engine which is available
    on most operating systems. For using this engine with Docling, Tesseract must be installed on your
    system, using the packaging tool of your choice. Below we provide example commands.
    After installing Tesseract you are expected to provide the path to its language files using the
    `TESSDATA_PREFIX` environment variable (note that it must terminate with a slash `/`).

    === "macOS (via [Homebrew](https://brew.sh/))"

        ```console
        brew install tesseract leptonica pkg-config
        TESSDATA_PREFIX=/opt/homebrew/share/tessdata/
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    === "Debian-based"

        ```console
        apt-get install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config
        TESSDATA_PREFIX=$(dpkg -L tesseract-ocr-eng | grep tessdata$)
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    === "RHEL"

        ```console
        dnf install tesseract tesseract-devel tesseract-langpack-eng tesseract-osd leptonica-devel
        TESSDATA_PREFIX=/usr/share/tesseract/tessdata/
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    <h4>Linking to Tesseract</h4>
    The most efficient usage of the Tesseract library is via linking. Docling is using
    the [Tesserocr](https://github.com/sirfz/tesserocr) package for this.

    If you get into installation issues of Tesserocr, we suggest using the following
    installation options:

    ```console
    pip uninstall tesserocr
    pip install --no-binary :all: tesserocr
    ```

## Development setup

To develop Docling features, bugfixes etc., install as follows from your local clone's root dir:

```bash
uv sync --all-extras
```


---

## Source References

- [`EasyOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L163) - Options for the EasyOCR engine.
- [`TesseractOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L201) - Options for the Tesseract engine.
- [`TesseractCliOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L185) - Options for the TesseractCli engine.
- [`OcrMacOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L216) - Options for the Mac OCR engine.
- [`RapidOcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L119) - Options for the RapidOCR engine.
- [`DocumentConverter`](https://github.com/docling-project/docling/blob/main/docling/document_converter.py#L178) - Convert documents of various input formats to Docling documents.


---

# ⚡ RTX GPU Acceleration

# ⚡ RTX GPU Acceleration

<div style="text-align: center">
    <img loading="lazy" alt="Docling on RTX" src="../../assets/nvidia_logo_green.svg" width="200px" />
</div>


Whether you're an AI enthusiast, researcher, or developer working with document processing, this guide will help you unlock the full potential of your NVIDIA RTX GPU with Docling.

By leveraging GPU acceleration, you can achieve up to **6x speedup** compared to CPU-only processing. This dramatic performance improvement makes GPU acceleration especially valuable for processing large batches of documents, handling high-throughput document conversion workflows, or experimenting with advanced document understanding models.

<!-- TBA. Performance improvement figure. -->

## Prerequisites

Before setting up GPU acceleration, ensure you have:

- An NVIDIA RTX GPU (RTX 40/50 series)
- Windows 10/11 or Linux operating system

## Installation Steps

### 1. Install NVIDIA GPU Drivers

First, ensure you have the latest NVIDIA GPU drivers installed:

- **Windows**: Download from [NVIDIA Driver Downloads](https://www.nvidia.com/Download/index.aspx)
- **Linux**: Use your distribution's package manager or download from NVIDIA

Verify the installation:

```bash
nvidia-smi
```

This command should display your GPU information and driver version.

### 2. Install CUDA Toolkit

CUDA is NVIDIA's parallel computing platform required for GPU acceleration.

Follow the official installation guide for your operating system at [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads). The installer will guide you through the process and automatically set up the required environment variables.

### 3. Install cuDNN

cuDNN provides optimized implementations for deep learning operations.

Follow the official installation guide at [NVIDIA cuDNN Downloads](https://developer.nvidia.com/cudnn). The guide provides detailed instructions for all supported platforms.

### 4. Install PyTorch with CUDA Support

To use GPU acceleration with Docling, you need to install PyTorch with CUDA support using the special `extra-index-url`:

```bash
# For CUDA 12.8 (current default for PyTorch)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# For CUDA 13.0
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
```

!!! note
    The `--index-url` parameter is crucial as it ensures you get the CUDA-enabled version of PyTorch instead of the CPU-only version.

For other CUDA versions and installation options, refer to the [PyTorch Installation Matrix](https://pytorch.org/get-started/locally/).

Verify PyTorch CUDA installation:

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

### 5. Install and Run Docling

Install Docling with all dependencies:

```bash
pip install docling
```

**That's it!** Docling will automatically detect and use your RTX GPU when available. No additional configuration is required for basic usage.

```python
from docling.document_converter import DocumentConverter

# Docling automatically uses GPU when available
converter = DocumentConverter()
result = converter.convert("document.pdf")
```

<details>
<summary><b>Advanced: Tuning GPU Performance</b></summary>

For optimal GPU performance with large document batches, you can adjust batch sizes and explicitly configure the accelerator:

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions

# Explicitly configure GPU acceleration
accelerator_options = AcceleratorOptions(
    device=AcceleratorDevice.CUDA,  # Use CUDA for NVIDIA GPUs
)

# Configure pipeline for optimal GPU performance
pipeline_options = ThreadedPdfPipelineOptions(
    ocr_batch_size=64,      # Increase batch size for GPU
    layout_batch_size=64,   # Increase batch size for GPU
    table_batch_size=4,
)

# Create converter with custom settings
converter = DocumentConverter(
    accelerator_options=accelerator_options,
    pipeline_options=pipeline_options,
)

# Convert documents
result = converter.convert("document.pdf")
```

Adjust batch sizes based on your GPU memory (see Performance Optimization Tips below).

</details>

## GPU-Accelerated VLM Pipeline

For maximum performance with Vision Language Models (VLM), you can run a local inference server on your RTX GPU. This approach provides significantly better throughput than inline VLM processing.

### Linux: Using vLLM (Recommended)

vLLM provides the best performance for GPU-accelerated VLM inference. Start the vLLM server with optimized parameters:

```bash
vllm serve ibm-granite/granite-docling-258M \
  --host 127.0.0.1 --port 8000 \
  --max-num-seqs 512 \
  --max-num-batched-tokens 8192 \
  --enable-chunked-prefill \
  --gpu-memory-utilization 0.9
```

### Windows: Using llama-server

On Windows, you can use `llama-server` from llama.cpp for GPU-accelerated VLM inference:

#### Installation

1. Download the latest llama.cpp release from the [GitHub releases page](https://github.com/ggml-org/llama.cpp/releases)
2. Extract the archive and locate `llama-server.exe`

#### Launch Command

```powershell
llama-server.exe `
  --hf-repo ibm-granite/granite-docling-258M-GGUF `
  -cb `
  -ngl -1 `
  --port 8000 `
  --context-shift `
  -np 16 -c 131072
```

!!! note "Performance Comparison"
    vLLM delivers approximately **4x better performance** compared to llama-server. For Windows users seeking maximum performance, consider running vLLM via WSL2 (Windows Subsystem for Linux). See [vLLM on RTX 5090 via Docker](https://github.com/BoltzmannEntropy/vLLM-5090) for detailed WSL2 setup instructions.

### Configure Docling for VLM Server

Once your inference server is running, configure Docling to use it:

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.settings import settings

BATCH_SIZE = 64

# Configure VLM options
vlm_options = vlm_model_specs.GRANITEDOCLING_VLLM_API
vlm_options.concurrency = BATCH_SIZE

# when running with llama.cpp (llama-server), use the different model name.
# vlm_options.params["model"] = "ibm-granite_granite-docling-258M-GGUF_granite-docling-258M-BF16.gguf"

# Set page batch size to match or exceed concurrency
settings.perf.page_batch_size = BATCH_SIZE

# Create converter with VLM pipeline
converter = DocumentConverter(
    pipeline_options=vlm_options,
)
```

For more details on VLM pipeline configuration, see the [GPU Support Guide](../usage/gpu.md).

## Performance Optimization Tips

### Batch Size Tuning

Adjust batch sizes based on your GPU memory:

- **RTX 5090 (32GB)**: Use batch sizes of 64-128
- **RTX 4090 (24GB)**: Use batch sizes of 32-64
- **RTX 5070 (12GB)**: Use batch sizes of 16-32

### Memory Management

Monitor GPU memory usage:

```python
import torch

# Check GPU memory
if torch.cuda.is_available():
    print(f"GPU Memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print(f"GPU Memory reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
```

## Troubleshooting

### CUDA Out of Memory

If you encounter out-of-memory errors:

1. Reduce batch sizes in `pipeline_options`
2. Process fewer documents concurrently
3. Clear GPU cache between batches:

```python
import torch
torch.cuda.empty_cache()
```

### CUDA Not Available

If `torch.cuda.is_available()` returns `False`:

1. Verify NVIDIA drivers are installed: `nvidia-smi`
2. Check CUDA installation: `nvcc --version`
3. Reinstall PyTorch with correct CUDA version
4. Ensure your GPU is CUDA-compatible

### Performance Not Improving

If GPU acceleration doesn't improve performance:

1. Increase batch sizes (if memory allows)
2. Ensure you're processing enough documents to benefit from GPU parallelization
3. Check GPU utilization: `nvidia-smi -l 1`
4. Verify PyTorch is using GPU: `torch.cuda.is_available()`

## Additional Resources

- [NVIDIA CUDA Documentation](https://docs.nvidia.com/cuda/)
- [PyTorch CUDA Installation Guide](https://pytorch.org/get-started/locally/)
- [Docling GPU Support Guide](../usage/gpu.md)
- [GPU Performance Examples](../examples/gpu_standard_pipeline.py)


---

# Quickstart

## Basic usage

### Python

In Docling, working with documents is as simple as:

1. converting your source file to a Docling document
2. using that Docling document for your workflow

For example, the snippet below shows conversion with export to Markdown:

```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # file path or URL
converter = DocumentConverter()
doc = converter.convert(source).document

print(doc.export_to_markdown())  # output: "### Docling Technical Report[...]"
```

Docling supports a wide array of [file formats](./supported_formats.md) and, as outlined in the
[architecture](../concepts/architecture.md) guide, provides a versatile document model along with a full suite of
supported operations.

### CLI

You can additionally use Docling directly from your terminal, for instance:

```console
docling https://arxiv.org/pdf/2206.01062
```

The CLI provides various options, such as 🥚[GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M) (incl. MLX acceleration) & other VLMs:
```bash
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
```

For all available options, run `docling --help` or check the [CLI reference](../reference/cli.md).

## What's next

Check out the Usage subpages (navigation menu on the left) as well as our [featured examples](../examples/index.md) for
additional usage workflows, including conversion customization, RAG, framework integrations, chunking, serialization,
enrichments, and much more!


---

# Supported Formats

Docling can parse various documents formats into a unified representation (Docling
Document), which it can export to different formats too — check out
[Architecture](../concepts/architecture.md) for more details.

Below you can find a listing of all supported input and output formats.

## Supported input formats

| Format | Description |
|--------|-------------|
| PDF | |
| DOCX, XLSX, PPTX | Default formats in MS Office 2007+, based on Office Open XML |
| Markdown | |
| AsciiDoc | Human-readable, plain-text markup language for structured technical content |
| HTML, XHTML | |
| CSV | |
| PNG, JPEG, TIFF, BMP, WEBP | Image formats |
| WebVTT | Web Video Text Tracks format for displaying timed text |

Schema-specific support:

| Format | Description |
|--------|-------------|
| USPTO XML | XML format followed by [USPTO](https://www.uspto.gov/patents) patents |
| JATS XML | XML format followed by [JATS](https://jats.nlm.nih.gov/) articles |
| Docling JSON | JSON-serialized [Docling Document](../concepts/docling_document.md) |

## Supported output formats

| Format | Description |
|--------|-------------|
| HTML | Both image embedding and referencing are supported |
| Markdown | |
| JSON | Lossless serialization of Docling Document |
| Text | Plain text, i.e. without Markdown markers |
| [Doctags](https://arxiv.org/pdf/2503.11576) | Markup format for efficiently representing the full content and layout characteristics of a document |


---

# Index

## Basic usage

### Python

In Docling, working with documents is as simple as:

1. converting your source file to a Docling document
2. using that Docling document for your workflow

For example, the snippet below shows conversion with export to Markdown:

```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # file path or URL
converter = DocumentConverter()
doc = converter.convert(source).document

print(doc.export_to_markdown())  # output: "### Docling Technical Report[...]"
```

Docling supports a wide array of [file formats](./supported_formats.md) and, as outlined in the
[architecture](../concepts/architecture.md) guide, provides a versatile document model along with a full suite of
supported operations.

### CLI

You can additionally use Docling directly from your terminal, for instance:

```console
docling https://arxiv.org/pdf/2206.01062
```

The CLI provides various options, such as 🥚[GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M) (incl. MLX acceleration) & other VLMs:
```bash
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
```

For all available options, run `docling --help` or check the [CLI reference](../reference/cli.md).

## What's next

Check out the Usage subpages (navigation menu on the left) as well as our [featured examples](../examples/index.md) for
additional usage workflows, including conversion customization, RAG, framework integrations, chunking, serialization,
enrichments, and much more!


---

# Jobkit

Docling's document conversion can be executed as distributed jobs using [Docling Jobkit](https://github.com/docling-project/docling-jobkit).

This library provides:

- Pipelines for running jobs with Kubeflow pipelines, Ray, or locally.
- Connectors to import and export documents via HTTP endpoints, S3, or Google Drive.

## Usage

### CLI

You can run Jobkit locally via the CLI:

```sh
uv run docling-jobkit-local [configuration-file-path]
```

The configuration file defines:

- Docling conversion options (e.g. OCR settings)
- Source location of input documents
- Target location for the converted outputs

Example configuration file:

```yaml
options:               # Example Docling's conversion options
  do_ocr: false         
sources:               # Source location (here Google Drive)
  - kind: google_drive
    path_id: 1X6B3j7GWlHfIPSF9VUkasN-z49yo1sGFA9xv55L2hSE
    token_path: "./dev/google_drive/google_drive_token.json" 
    credentials_path: "./dev/google_drive/google_drive_credentials.json"  
target:                # Target location (here S3)
  kind: s3
  endpoint: localhost:9000
  verify_ssl: false
  bucket: docling-target
  access_key: minioadmin
  secret_key: minioadmin
```

## Connectors

Connectors are used to import documents for processing with Docling and to export results after conversion.

The currently supported connectors are:

- HTTP endpoints
- S3
- Google Drive

### Google Drive

To use Google Drive as a source or target, you need to enable the API and set up credentials.

Step 1: Enable the [Google Drive API](https://console.cloud.google.com/apis/enableflow?apiid=drive.googleapis.com).

- Go to the Google [Cloud Console](https://console.cloud.google.com/).
- Search for “Google Drive API” and enable it.

Step 2: [Create OAuth credentials](https://developers.google.com/workspace/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application). 

- Go to APIs & Services > Credentials.
- Click “+ Create credentials” > OAuth client ID.
- If prompted, configure the OAuth consent screen with "Audience: External".
- Select application type: "Desktop app".
- Create the application
- Download the credentials JSON and rename it to `google_drive_credentials.json`.

Step 3: Add test users.

- Go to OAuth consent screen > Test users.
- Add your email address.

Step 4: Edit configuration file.

- Edit `credentials_path` with your path to `google_drive_credentials.json`.
- Edit `path_id` with your source or target location. It can be obtained from the URL as follows:
    - Folder: `https://drive.google.com/drive/u/0/folders/1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5` > folder id is `1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5`.
    - File: `https://docs.google.com/document/d/1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw/edit` > document id is `1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw`.

Step 5: Authenticate via CLI.

- Run the CLI with your configuration file.
- A browser window will open for authentication and gerate a token file that will be save on the configured `token_path` and reused for next runs.


---

# Advanced Options

## Model prefetching and offline usage

By default, models are downloaded automatically upon first usage. If you would prefer
to explicitly prefetch them for offline use (e.g. in air-gapped environments) you can do
that as follows:

**Step 1: Prefetch the models**

Use the `docling-tools models download` utility:

```sh
$ docling-tools models download
Downloading layout model...
Downloading tableformer model...
Downloading picture classifier model...
Downloading code formula model...
Downloading easyocr models...
Models downloaded into $HOME/.cache/docling/models.
```

Alternatively, models can be programmatically downloaded using `docling.utils.model_downloader.download_models()`.

Also, you can use `download-hf-repo` parameter to download arbitrary models from HuggingFace by specifying repo id:

```sh
$ docling-tools models download-hf-repo ds4sd/SmolDocling-256M-preview
Downloading ds4sd/SmolDocling-256M-preview model from HuggingFace...
```

**Step 2: Use the prefetched models**

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

artifacts_path = "/local/path/to/models"

pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Or using the CLI:

```sh
docling --artifacts-path="/local/path/to/models" FILE
```

Or using the `DOCLING_ARTIFACTS_PATH` environment variable:

```sh
export DOCLING_ARTIFACTS_PATH="/local/path/to/models"
python my_docling_script.py
```

## Using remote services

The main purpose of Docling is to run local models which are not sharing any user data with remote services.
Anyhow, there are valid use cases for processing part of the pipeline using remote services, for example invoking OCR engines from cloud vendors or the usage of hosted LLMs.

In Docling we decided to allow such models, but we require the user to explicitly opt-in in communicating with external services.

```py
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions(enable_remote_services=True)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

When the value `enable_remote_services=True` is not set, the system will raise an exception `OperationNotAllowed()`.

_Note: This option is only related to the system sending user data to remote services. Control of pulling data (e.g. model weights) follows the logic described in [Model prefetching and offline usage](#model-prefetching-and-offline-usage)._

### List of remote model services

The options in this list require the explicit `enable_remote_services=True` when processing the documents.

- [`PictureDescriptionApiOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L238): Using vision models via API calls.


## Adjust pipeline features

The example file [custom_convert.py](../examples/custom_convert.py) contains multiple ways
one can adjust the conversion pipeline and features.

### Control PDF table extraction options

You can control if table structure recognition should map the recognized structure back to PDF cells (default) or use text cells from the structure prediction itself.
This can improve output quality if you find that multiple columns in extracted tables are erroneously merged into one.


```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False  # uses text cells predicted from table structure model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Since docling 1.16.0: You can control which TableFormer mode you want to use. Choose between `TableFormerMode.FAST` (faster but less accurate) and `TableFormerMode.ACCURATE` (default) to receive better quality with difficult table structures.

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # use more accurate TableFormer model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```


## Impose limits on the document size

You can limit the file size and number of pages which should be allowed to process per document:

```python
from pathlib import Path
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source, max_num_pages=100, max_file_size=20971520)
```

## Convert from binary PDF streams

You can convert PDFs from a binary stream instead of from the filesystem as follows:

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

buf = BytesIO(your_binary_stream)
source = DocumentStream(name="my_doc.pdf", stream=buf)
converter = DocumentConverter()
result = converter.convert(source)
```

## Limit resource usage

You can limit the CPU threads used by Docling by setting the environment variable `OMP_NUM_THREADS` accordingly. The default setting is using 4 CPU threads.


---

## Source References

- [`PictureDescriptionApiOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L238)


---

# Vision Models


The [`VlmPipeline`](https://github.com/docling-project/docling/blob/main/docling/pipeline/vlm_pipeline.py#L51) in Docling allows you to convert documents end-to-end using a vision-language model.

Docling supports vision-language models which output:

- DocTags (e.g. [SmolDocling](https://huggingface.co/ds4sd/SmolDocling-256M-preview)), the preferred choice
- Markdown
- HTML


For running Docling using local models with the [`VlmPipeline`](https://github.com/docling-project/docling/blob/main/docling/pipeline/vlm_pipeline.py#L51):

=== "CLI"

    ```bash
    docling --pipeline vlm FILE
    ```

=== "Python"

    See also the example [minimal_vlm_pipeline.py](./../examples/minimal_vlm_pipeline.py).

    ```python
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.pipeline.vlm_pipeline import VlmPipeline

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )

    doc = converter.convert(source="FILE").document
    ```

## Available local models

By default, the vision-language models are running locally.
Docling allows to choose between the Hugging Face [Transformers](https://github.com/huggingface/transformers) framework and the [MLX](https://github.com/Blaizzy/mlx-vlm) (for Apple devices with MPS acceleration) one.

The following table reports the models currently available out-of-the-box.

| Model instance | Model | Framework | Device | Num pages | Inference time (sec) |
| ---------------|------ | --------- | ------ | --------- | ---------------------|
| `vlm_model_specs.GRANITEDOCLING_TRANSFORMERS` | [ibm-granite/granite-docling-258M](https://huggingface.co/ibm-granite/granite-docling-258M) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  - |
| `vlm_model_specs.GRANITEDOCLING_MLX` | [ibm-granite/granite-docling-258M-mlx-bf16](https://huggingface.co/ibm-granite/granite-docling-258M-mlx-bf16) | `MLX`| MPS | 1 |    - |
| `vlm_model_specs.SMOLDOCLING_TRANSFORMERS` | [ds4sd/SmolDocling-256M-preview](https://huggingface.co/ds4sd/SmolDocling-256M-preview) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  102.212 |
| `vlm_model_specs.SMOLDOCLING_MLX` | [ds4sd/SmolDocling-256M-preview-mlx-bf16](https://huggingface.co/ds4sd/SmolDocling-256M-preview-mlx-bf16) | `MLX`| MPS | 1 |    6.15453 |
| `vlm_model_specs.QWEN25_VL_3B_MLX` | [mlx-community/Qwen2.5-VL-3B-Instruct-bf16](https://huggingface.co/mlx-community/Qwen2.5-VL-3B-Instruct-bf16)  |  `MLX`| MPS | 1 |   23.4951 |
| `vlm_model_specs.PIXTRAL_12B_MLX` | [mlx-community/pixtral-12b-bf16](https://huggingface.co/mlx-community/pixtral-12b-bf16) |  `MLX` | MPS | 1 |  308.856 |
| `vlm_model_specs.GEMMA3_12B_MLX` | [mlx-community/gemma-3-12b-it-bf16](https://huggingface.co/mlx-community/gemma-3-12b-it-bf16) |  `MLX` | MPS | 1 |  378.486 |
| `vlm_model_specs.GRANITE_VISION_TRANSFORMERS` | [ibm-granite/granite-vision-3.2-2b](https://huggingface.co/ibm-granite/granite-vision-3.2-2b) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  104.75 |
| `vlm_model_specs.PHI4_TRANSFORMERS` | [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | `Transformers/AutoModelForCasualLM` | CPU | 1 | 1175.67 |
| `vlm_model_specs.PIXTRAL_12B_TRANSFORMERS` | [mistral-community/pixtral-12b](https://huggingface.co/mistral-community/pixtral-12b) | `Transformers/AutoModelForVision2Seq` | CPU | 1 | 1828.21 |

_Inference time is computed on a Macbook M3 Max using the example page `tests/data/pdf/2305.03393v1-pg9.pdf`. The comparison is done with the example [compare_vlm_models.py](./../examples/compare_vlm_models.py)._

For choosing the model, the code snippet above can be extended as follow

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from docling.datamodel import vlm_model_specs

pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.SMOLDOCLING_MLX,  # <-- change the model here
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        ),
    }
)

doc = converter.convert(source="FILE").document
```

### Other models

Other models can be configured by directly providing the Hugging Face `repo_id`, the prompt and a few more options.

For example:

```python
from docling.datamodel.pipeline_options_vlm_model import InlineVlmOptions, InferenceFramework, TransformersModelType

pipeline_options = VlmPipelineOptions(
    vlm_options=InlineVlmOptions(
        repo_id="ibm-granite/granite-vision-3.2-2b",
        prompt="Convert this page to markdown. Do not miss any text and only output the bare markdown!",
        response_format=ResponseFormat.MARKDOWN,
        inference_framework=InferenceFramework.TRANSFORMERS,
        transformers_model_type=TransformersModelType.AUTOMODEL_VISION2SEQ,
        supported_devices=[
            AcceleratorDevice.CPU,
            AcceleratorDevice.CUDA,
            AcceleratorDevice.MPS,
            AcceleratorDevice.XPU,
        ],
        scale=2.0,
        temperature=0.0,
    )
)
```


## Remote models

Additionally to local models, the [`VlmPipeline`](https://github.com/docling-project/docling/blob/main/docling/pipeline/vlm_pipeline.py#L51) allows to offload the inference to a remote service hosting the models.
Many remote inference services are provided, the key requirement is to offer an OpenAI-compatible API. This includes vLLM, Ollama, etc.

More examples on how to connect with the remote inference services can be found in the following examples:

- [vlm_pipeline_api_model.py](./../examples/vlm_pipeline_api_model.py)


---

## Source References

- [`VlmPipeline`](https://github.com/docling-project/docling/blob/main/docling/pipeline/vlm_pipeline.py#L51)


---

# GPU support

# GPU support

## Achieving Optimal GPU Performance with Docling

This guide describes how to maximize GPU performance for Docling pipelines. It covers device selection, pipeline differences, and provides example snippets for configuring batch size and concurrency in the VLM pipeline for both Linux and Windows.

!!! note

    Improvements and optimizations strategies for maximizing the GPU performance is an
    active topic. Regularly check these guidelines for updates.


### Standard Pipeline

Enable GPU acceleration by configuring the accelerator device and concurrency options using Docling's API:

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions

# Configure accelerator options for GPU
accelerator_options = AcceleratorOptions(
    device=AcceleratorDevice.CUDA,  # or AcceleratorDevice.AUTO
)
```

Batch size and concurrency for document processing are controlled for each stage of the pipeline as:

```python
from docling.datamodel.pipeline_options import (
    ThreadedPdfPipelineOptions,
)

pipeline_options = ThreadedPdfPipelineOptions(
    ocr_batch_size=64,  # default 4
    layout_batch_size=64,  # default 4
    table_batch_size=4,  # currently not using GPU batching
)
```

Setting a higher `page_batch_size` will run the Docling models (in particular the layout detection stage) with a GPU batch inference mode.

#### Complete example

For a complete example see [gpu_standard_pipeline.py](../examples/gpu_standard_pipeline.py).

#### OCR engines

The current Docling OCR engines rely on third-party libraries, hence GPU support depends on the availability in the respective engines.

The only setup which is known to work at the moment is RapidOCR with the torch backend, which can be enabled via

```py
pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options = RapidOcrOptions(
    backend="torch",
)
```

More details in the GitHub discussion [#2451](https://github.com/docling-project/docling/discussions/2451).


### VLM Pipeline

For best GPU utilization, use a local inference server. Docling supports inference servers which exposes the OpenAI-compatible chat completion endpoints. For example:

- vllm: `http://localhost:8000/v1/chat/completions` (available only on Linux)
- LM Studio: `http://localhost:1234/v1/chat/completions` (available both on Linux and Windows)
- Ollama: `http://localhost:11434/v1/chat/completions` (available both on Linux and Windows)


#### Start the inference server

Here is an example on how to start the [vllm](https://docs.vllm.ai/) inference server with optimum parameters for Granite Docling.

```sh
vllm serve ibm-granite/granite-docling-258M \
  --host 127.0.0.1 --port 8000 \
  --max-num-seqs 512 \
  --max-num-batched-tokens 8192 \
  --enable-chunked-prefill \
  --gpu-memory-utilization 0.9
```

#### Configure Docling

Configure the VLM pipeline using Docling's VLM options:

```python
from docling.datamodel.pipeline_options import VlmPipelineOptions

vlm_options = VlmPipelineOptions(
    enable_remote_services=True,
    vlm_options={
        "url": "http://localhost:8000/v1/chat/completions",  # or any other compatible endpoint
        "params": {
            "model": "ibm-granite/granite-docling-258M",
            "max_tokens": 4096,
        },
        "concurrency": 64,  # default is 1
        "prompt": "Convert this page to docling.",
        "timeout": 90,
    }
)
```

Additionally to the concurrency, we also have to set the `page_batch_size` Docling parameter. Make sure to set `settings.perf.page_batch_size >= vlm_options.concurrency`.

```python
from docling.datamodel.settings import settings

settings.perf.page_batch_size = 64  # default is 4
```

#### Complete example

For a complete example see [gpu_vlm_pipeline.py](../examples/gpu_vlm_pipeline.py).


#### Available models

Both LM Studio and Ollama rely on llama.cpp as runtime engine. For using this engine, models have to be converted to the gguf format.

Here is a list of known models which are available in gguf format and how to use them.

TBA.

## Performance results

### Test data

| | PDF doc | [ViDoRe V3 HR](https://huggingface.co/datasets/vidore/vidore_v3_hr) |
| - | - | - |
| Num docs | 1 | 14 |
| Num pages | 192 | 1110 |
| Num tables | 95 | 258 |
| Format type | PDF | Parquet of images |


### Test infrastructure

| | g6e.2xlarge | RTX 5090 | RTX 5070 |
| - | - | - | - |
| Description | AWS instance `g6e.2xlarge` | Linux bare metal machine | Windows 11 bare metal machine |
| CPU | 8 vCPUs, AMD EPYC 7R13 | 16 vCPU, AMD Ryzen 7 9800 | 16 vCPU, AMD Ryzen 7 9800 |
| RAM | 64GB | 128GB | 64GB |
| GPU | NVIDIA L40S 48GB | NVIDIA GeForce RTX 5090 | NVIDIA GeForce RTX 5070 |
| CUDA Version | 13.0, driver 580.95.05 | 13.0, driver 580.105.08 | 13.0, driver 581.57 |


### Results

<table>
  <thead>
    <tr><th rowspan="2">Pipeline</th><th colspan="2">g6e.2xlarge</th><th colspan="2">RTX 5090</th><th colspan="2">RTX 5070</th></tr>
    <tr><th>PDF doc</th><th>ViDoRe V3 HR</th><th>PDF doc</th><th>ViDoRe V3 HR</th><th>PDF doc</th><th>ViDoRe V3 HR</th></tr>
  </thead>
  <tbody>
    <tr><td>Standard - Inline (no OCR)</td><td>3.1 pages/second</td><td>-</td><td>7.9 pages/second<br /><small><em>[cpu-only]* 1.5 pages/second</em></small></td><td>-</td><td>4.2 pages/second<br /><small><em>[cpu-only]* 1.2 pages/second</em></small></td><td>-</td></tr>
    <tr><td>Standard - Inline (with OCR)</td><td></td><td></td><td>tba</td><td>1.6 pages/second</td><td>tba</td><td>1.1 pages/second</td></tr>
    <tr><td>VLM - Inference server (GraniteDocling)</td><td>2.4 pages/second</td><td>-</td><td>3.8 pages/second</td><td>3.6-4.5 pages/second</td><td>2.0 pages/second</td><td>2.8-3.2 pages/second</td></tr>
  </tbody>
</table>

_* cpu-only timing computed with 16 pytorch threads._


---

# Enable connections to remote services

Docling allows to enrich the conversion pipeline with additional steps which process specific document components,
e.g. code blocks, pictures, etc. The extra steps usually require extra models executions which may increase
the processing time consistently. For this reason most enrichment models are disabled by default.

The following table provides an overview of the default enrichment models available in Docling.

| Feature | Parameter | Processed item | Description |
| ------- | --------- | ---------------| ----------- |
| Code understanding | `do_code_enrichment` | `CodeItem` | See [docs below](#code-understanding). |
| Formula understanding | `do_formula_enrichment` | `TextItem` with label `FORMULA` | See [docs below](#formula-understanding). |
| Picture classification | `do_picture_classification` | `PictureItem` | See [docs below](#picture-classification). |
| Picture description | `do_picture_description` | `PictureItem` | See [docs below](#picture-description). |


## Enrichments details

### Code understanding

The code understanding step allows to use advanced parsing for code blocks found in the document.
This enrichment model also set the `code_language` property of the `CodeItem`.

Model specs: see the [`CodeFormula` model card](https://huggingface.co/ds4sd/CodeFormula).

Example command line:

```sh
docling --enrich-code FILE
```

Example code:

```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```

### Formula understanding

The formula understanding step will analyze the equation formulas in documents and extract their LaTeX representation.
The HTML export functions in the DoclingDocument will leverage the formula and visualize the result using the mathml html syntax.

Model specs: see the [`CodeFormula` model card](https://huggingface.co/ds4sd/CodeFormula).

Example command line:

```sh
docling --enrich-formula FILE
```

Example code:

```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```

### Picture classification

The picture classification step classifies the `PictureItem` elements in the document with the `DocumentFigureClassifier` model.
This model is specialized to understand the classes of pictures found in documents, e.g. different chart types, flow diagrams,
logos, signatures, etc.

Model specs: see the [`DocumentFigureClassifier` model card](https://huggingface.co/ds4sd/DocumentFigureClassifier).

Example command line:

```sh
docling --enrich-picture-classes FILE
```

Example code:

```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2
pipeline_options.do_picture_classification = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```


### Picture description

The picture description step allows to annotate a picture with a vision model. This is also known as a "captioning" task.
The Docling pipeline allows to load and run models completely locally as well as connecting to remote API which support the chat template.
Below follow a few examples on how to use some common vision model and remote services.


```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document

```

#### Granite Vision model

Model specs: see the [`ibm-granite/granite-vision-3.1-2b-preview` model card](https://huggingface.co/ibm-granite/granite-vision-3.1-2b-preview).

Usage in Docling:

```py
from docling.datamodel.pipeline_options import granite_picture_description

pipeline_options.picture_description_options = granite_picture_description
```

#### SmolVLM model

Model specs: see the [`HuggingFaceTB/SmolVLM-256M-Instruct` model card](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct).

Usage in Docling:

```py
from docling.datamodel.pipeline_options import smolvlm_picture_description

pipeline_options.picture_description_options = smolvlm_picture_description
```

#### Other vision models

The option class [`PictureDescriptionVlmOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L251) allows to use any another model from the Hugging Face Hub.

```py
from docling.datamodel.pipeline_options import PictureDescriptionVlmOptions

pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="",  # <-- add here the Hugging Face repo_id of your favorite VLM
    prompt="Describe the image in three sentences. Be concise and accurate.",
)
```

#### Remote vision model

The option class [`PictureDescriptionApiOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L238) allows to use models hosted on remote platforms, e.g.
on local endpoints served by [VLLM](https://docs.vllm.ai), [Ollama](https://ollama.com/) and others,
or cloud providers like [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai), etc.

_Note: in most cases this option will send your data to the remote service provider._

Usage in Docling:

```py
from docling.datamodel.pipeline_options import PictureDescriptionApiOptions

# Enable connections to remote services
pipeline_options.enable_remote_services=True  # <-- this is required!

# Example using a model running locally, e.g. via VLLM
# $ vllm serve MODEL_NAME
pipeline_options.picture_description_options = PictureDescriptionApiOptions(
    url="http://localhost:8000/v1/chat/completions",
    params=dict(
        model="MODEL NAME",
        seed=42,
        max_completion_tokens=200,
    ),
    prompt="Describe the image in three sentences. Be concise and accurate.",
    timeout=90,
)
```

End-to-end code snippets for cloud providers are available in the examples section:

- [IBM watsonx.ai](../examples/pictures_description_api.py)


## Develop new enrichment models

Besides looking at the implementation of all the models listed above, the Docling documentation has a few examples
dedicated to the implementation of enrichment models.

- [Develop picture enrichment](../examples/develop_picture_enrichment.py)
- [Develop formula enrichment](../examples/develop_formula_understanding.py)


---

## Source References

- [`PictureDescriptionVlmOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L251)
- [`PictureDescriptionApiOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L238)


---

# Mcp

New AI trends focus on Agentic AI, an artificial intelligence system that can accomplish a specific goal with limited supervision.
Agents can act autonomously to understand, plan, and execute a specific task.

To address the integration problem, the [Model Context Protocol](https://modelcontextprotocol.io) (MCP) emerges as a popular standard for connecting AI applications to external tools.

## Docling MCP

Docling supports the development of AI agents by providing an MCP Server. It allows you to experiment with document processing in different MCP Clients. Adding [Docling MCP](https://github.com/docling-project/docling-mcp) in your favorite client is usually as simple as adding the following entry in the configuration file:

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": [
        "--from=docling-mcp",
        "docling-mcp-server"
      ]
    }
  }
}
```

When using [Claude on your desktop](https://claude.ai/download), just edit the config file `claude_desktop_config.json` with the snippet above or the example provided [here](https://github.com/docling-project/docling-mcp/blob/main/docs/integrations/claude_desktop_config.json).

In **[LM Studio](https://lmstudio.ai/)**, edit the `mcp.json` file with the appropriate section or simply click on the button below for a direct install.

[![Add MCP Server docling to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](https://lmstudio.ai/install-mcp?name=docling&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb209ZG9jbGluZy1tY3AiLCJkb2NsaW5nLW1jcC1zZXJ2ZXIiXX0%3D)


Docling MCP also provides tools specific for some applications and frameworks. See the [Docling MCP](https://github.com/docling-project/docling-mcp) Server repository for more details. You will find examples of building agents powered by Docling capabilities and leveraging frameworks like [LlamaIndex](https://www.llamaindex.ai/), [Llama Stack](https://github.com/llamastack/llama-stack), [Pydantic AI](https://ai.pydantic.dev/), or [smolagents](https://github.com/huggingface/smolagents).


---

# Index

In this space, you can explore numerous Docling application recipes & end-to-end workflows!

Here some of our picks to get you started:

- 🔀 conversion examples ranging from [simple conversion to Markdown](./minimal.py) and export of [figures](./export_figures.py) & [tables](./export_tables.py), to [VLM](./minimal_vlm_pipeline.py) and [audio](./minimal_asr_pipeline.py) pipelines
- 💬 various RAG examples, e.g. based on [LangChain](./rag_langchain.ipynb), [LlamaIndex](./rag_llamaindex.ipynb), or [Haystack](./rag_haystack.ipynb), including [visual grounding](./visual_grounding.ipynb), and using different vector stores like [Milvus](./rag_milvus.ipynb), [Weaviate](./rag_weaviate.ipynb), or [Qdrant](./retrieval_qdrant.ipynb)
- 📤 [{==\[:fontawesome-solid-flask:{ title="beta feature" } beta\]==} structured data extraction](./extraction.ipynb)
- examples for ✍️ [serialization](./serialization.ipynb) and ✂️ [chunking](./hybrid_chunking.ipynb), including [user-defined customizations](./advanced_chunking_and_serialization.ipynb)
- 🖼️ [picture annotations](./pictures_description.ipynb) and [enrichments](./enrich_doclingdocument.py)

👈 ... and there is much more: explore all the examples using the navigation menu on the side

<div class="grid" style="text-align: center">
    <div class="card">
        Visual grounding
        <hr />
        <img loading="lazy" alt="RAG with visual grounding" src="../assets/visual_grounding.png" height="150px" />
    </div>
    <div class="card">
        Picture annotations
        <hr />
        <img loading="lazy" alt="Picture annotation" src="../assets/picture_annotations.png" height="150px" />
    </div>
</div>


---

# FAQ

# FAQ

This is a collection of FAQ collected from the user questions on <https://github.com/docling-project/docling/discussions>.


??? question "Is Python 3.14 supported?"

    ### Is Python 3.14 supported?

    Python 3.14 is supported from Docling 2.59.0.


??? question "Is Python 3.13 supported?"

    ### Is Python 3.13 supported?

    Python 3.13 is supported from Docling 2.18.0.


??? question "Install conflicts with numpy (python 3.13)"

    ### Install conflicts with numpy (python 3.13)

    When using `docling-ibm-models>=2.0.7` and `deepsearch-glm>=0.26.2` these issues should not show up anymore.
    Docling supports numpy versions `>=1.24.4,<3.0.0` which should match all usages.

    **For older versions**

    This has been observed installing docling and langchain via poetry.

    ```
    ...
    Thus, docling (>=2.7.0,<3.0.0) requires numpy (>=1.26.4,<2.0.0).
    So, because ... depends on both numpy (>=2.0.2,<3.0.0) and docling (^2.7.0), version solving failed.
    ```

    Numpy is only adding Python 3.13 support starting in some 2.x.y version. In order to prepare for 3.13, Docling depends on a 2.x.y for 3.13, otherwise depending an 1.x.y version. If you are allowing 3.13 in your pyproject.toml, Poetry will try to find some way to reconcile Docling's numpy version for 3.13 (some 2.x.y) with LangChain's version for that (some 1.x.y) — leading to the error above.

    Check if Python 3.13 is among the Python versions allowed by your pyproject.toml and if so, remove it and try again.
    E.g., if you have python = "^3.10", use python = ">=3.10,<3.13" instead.

    If you want to retain compatibility with python 3.9-3.13, you can also use a selector in pyproject.toml similar to the following

    ```toml
    numpy = [
        { version = "^2.1.0", markers = 'python_version >= "3.13"' },
        { version = "^1.24.4", markers = 'python_version < "3.13"' },
    ]
    ```

    Source: Issue [#283](https://github.com/docling-project/docling/issues/283#issuecomment-2465035868)


??? question "Is macOS x86_64 supported?"

    ### Is macOS x86_64 supported?

    Yes, Docling (still) supports running the standard pipeline on macOS x86_64.

    However, users might get into a combination of incompatible dependencies on a fresh install.
    Because Docling depends on PyTorch which dropped support for macOS x86_64 after the 2.2.2 release,
    and this old version of PyTorch works only with NumPy 1.x, users **must** ensure the correct NumPy version is running.

    ```shell
    pip install docling "numpy<2.0.0"
    ```

    Source: Issue [#1694](https://github.com/docling-project/docling/issues/1694).


??? question "I get this error ImportError: libGL.so.1: cannot open shared object file: No such file or directory"

    ### I get this error ImportError: libGL.so.1: cannot open shared object file: No such file or directory

    This error orginates from conflicting OpenCV distribution in some Docling third-party dependencies.
    `opencv-python` and `opencv-python-headless` both define the same python package `cv2` and, if installed together,
    this often creates conflicts. Moreover, the `opencv-python` package (which is more common) depends on the OpenGL UI
    framework, which is usually not included for headless environments like Docker containers or remote VMs.

    When you encouter the error above, you have two possibilities.

    Solution 1: Force the headless OpenCV (preferred)

    ```sh
    pip uninstall -y opencv-python opencv-python-headless
    pip install --no-cache-dir opencv-python-headless
    ```

    Solution 2: Install the libGL system dependency.

    === "Debian-based"

        ```console
        apt-get install libgl1
        ```

    === "RHEL / Fedora"

        ```console
        dnf install mesa-libGL
        ```


??? question "Are text styles (bold, underline, etc) supported?"

    ### Are text styles (bold, underline, etc) supported?

    Text styles are supported in the `DoclingDocument` format.
    Currently only the declarative backends (i.e. the ones used for docx, pptx, markdown, html, etc) are able to set
    the correct text styles. Support for PDF is not yet possible.


??? question "How do I run completely offline?"

    ### How do I run completely offline?

    Docling is not using any remote service, hence it can run in completely isolated air-gapped environments.

    The only requirement is pointing the Docling runtime to the location where the model artifacts have been stored.

    For example

    ```py

    pipeline_options = PdfPipelineOptions(artifacts_path="your location")
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    ```

    Source: Issue [#326](https://github.com/docling-project/docling/issues/326)


??? question " Which model weights are needed to run Docling?"
    ### Which model weights are needed to run Docling?

    Model weights are needed for the AI models used in the PDF pipeline. Other document types (docx, pptx, etc) do not have any such requirement.

    For processing PDF documents, Docling requires the model weights from <https://huggingface.co/ds4sd/docling-models>.

    When OCR is enabled, some engines also require model artifacts. For example EasyOCR, for which Docling has [special pipeline options](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L68) to control the runtime behavior.


??? question "SSL error downloading model weights"

    ### SSL error downloading model weights

    ```
    URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)>
    ```

    Similar SSL download errors have been observed by some users. This happens when model weights are fetched from Hugging Face.
    The error could happen when the python environment doesn't have an up-to-date list of trusted certificates.

    Possible solutions were

    - Update to the latest version of [certifi](https://pypi.org/project/certifi/), i.e. `pip install --upgrade certifi`
    - Use [pip-system-certs](https://pypi.org/project/pip-system-certs/) to use the latest trusted certificates on your system.
    - Set environment variables `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` to the value of `python -m certifi`:
        ```
        CERT_PATH=$(python -m certifi)
        export SSL_CERT_FILE=${CERT_PATH}
        export REQUESTS_CA_BUNDLE=${CERT_PATH}
        ```


??? question "Which OCR languages are supported?"

    ### Which OCR languages are supported?

    Docling supports multiple OCR engine, each one has its own list of supported languages.
    Here is a collection of links to the original OCR engine's documentation listing the OCR languages.

    - [EasyOCR](https://www.jaided.ai/easyocr/)
    - [Tesseract](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)
    - [RapidOCR](https://rapidai.github.io/RapidOCRDocs/blog/2022/09/28/%E6%94%AF%E6%8C%81%E8%AF%86%E5%88%AB%E8%AF%AD%E8%A8%80/)
    - [Mac OCR](https://github.com/straussmaximilian/ocrmac/tree/main?tab=readme-ov-file#example-select-language-preference)

    Setting the OCR language in Docling is done via the OCR pipeline options:

    ```py
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    pipeline_options = PdfPipelineOptions()
    pipeline_options.ocr_options.lang = ["fr", "de", "es", "en"]  # example of languages for EasyOCR
    ```


??? question "Some images are missing from MS Word and Powerpoint"

    ### Some images are missing from MS Word and Powerpoint

    The image processing library used by Docling is able to handle embedded WMF images only on Windows platform.
    If you are on other operating systems, these images will be ignored.


??? question "`HybridChunker` triggers warning: 'Token indices sequence length is longer than the specified maximum sequence length for this model'"

    ### `HybridChunker` triggers warning: 'Token indices sequence length is longer than the specified maximum sequence length for this model'

    **TLDR**:
    In the context of the `HybridChunker`, this is a known & ancitipated "false alarm".

    **Details**:

    Using the [`HybridChunker`](../concepts/chunking.md#hybrid-chunker) often triggers a warning like this:
    > Token indices sequence length is longer than the specified maximum sequence length for this model (531 > 512). Running this sequence through the model will result in indexing errors

    This is a warning that is emitted by transformers, saying that actually *running this sequence through the model* will result in indexing errors, i.e. the problematic case is only if one indeed passes the particular sequence through the (embedding) model.

    In our case though, this occurs as a "false alarm", since what happens is the following:

    - the chunker invokes the tokenizer on a potentially long sequence (e.g. 530 tokens as mentioned in the warning) in order to count its tokens, i.e. to assess if it is short enough. At this point transformers already emits the warning above!
    - whenever the sequence at hand is oversized, the chunker proceeds to split it (but the transformers warning has already been shown nonetheless)

    What is important is the actual token length of the produced chunks.
    The snippet below can be used for getting the actual maximum chunk size (for users wanting to confirm that this does not exceed the model limit):

    ```python
    chunk_max_len = 0
    for i, chunk in enumerate(chunks):
        ser_txt = chunker.serialize(chunk=chunk)
        ser_tokens = len(tokenizer.tokenize(ser_txt))
        if ser_tokens > chunk_max_len:
            chunk_max_len = ser_tokens
        print(f"{i}\t{ser_tokens}\t{repr(ser_txt[:100])}...")
    print(f"Longest chunk yielded: {chunk_max_len} tokens")
    print(f"Model max length: {tokenizer.model_max_length}")
    ```

    Also see [docling#725](https://github.com/docling-project/docling/issues/725).

    Source: Issue [docling-core#119](https://github.com/docling-project/docling-core/issues/119)


??? question "How to use flash attention?"

    ### How to use flash attention?

    When running models in Docling on CUDA devices, you can enable the usage of the Flash Attention2 library.

    Using environment variables:

    ```
    DOCLING_CUDA_USE_FLASH_ATTENTION2=1
    ```

    Using code:

    ```python
    from docling.datamodel.accelerator_options import (
        AcceleratorOptions,
    )

    pipeline_options = VlmPipelineOptions(
        accelerator_options=AcceleratorOptions(cuda_use_flash_attention2=True)
    )
    ```

    This requires having the [flash-attn](https://pypi.org/project/flash-attn/) package installed. Below are two alternative ways for installing it:

    ```shell
    # Building from sources (required the CUDA dev environment)
    pip install flash-attn

    # Using pre-built wheels (not available in all possible setups)
    FLASH_ATTENTION_SKIP_CUDA_BUILD=TRUE pip install flash-attn
    ```


---

# Docling Document

# Docling Document

This is an automatic generated API reference of the DoclingDocument type.

::: docling_core.types.doc
    handler: python
    options:
        members:
            - DoclingDocument
            - DocumentOrigin
            - DocItem
            - DocItemLabel
            - ProvenanceItem
            - GroupItem
            - GroupLabel
            - NodeItem
            - PageItem
            - FloatingItem
            - TextItem
            - TableItem
            - TableCell
            - TableData
            - TableCellLabel
            - KeyValueItem
            - SectionHeaderItem
            - PictureItem
            - ImageRef
            - PictureClassificationClass
            - PictureClassificationData
            - RefItem
            - BoundingBox
            - CoordOrigin
            - ImageRefMode
            - Size
        docstring_style: sphinx
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        show_root_toc_entry: true
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        show_labels: false
        signature_crossrefs: true
        summary: true


---

# CLI reference

# CLI reference

This page provides documentation for our command line tools.

::: mkdocs-click
    :module: docling.cli.main
    :command: click_app
    :prog_name: docling
    :style: table


---

# Document converter

# Document converter

This is an automatic generated API reference of the main components of Docling.

::: docling.document_converter
    handler: python
    options:
        members:
            - DocumentConverter
            - ConversionResult
            - ConversionStatus
            - FormatOption
            - InputFormat
            - PdfFormatOption
            - ImageFormatOption
            - StandardPdfPipeline
            - WordFormatOption
            - PowerpointFormatOption
            - MarkdownFormatOption
            - AsciiDocFormatOption
            - HTMLFormatOption
            - SimplePipeline
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_[^_]"]
        heading_level: 2
        inherited_members: true
        docstring_options:
            ignore_init_summary: true
        show_docstring_attributes: false
        show_attribute_values: false
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        signature_crossrefs: true
        summary: true


---

# Pipeline options

# Pipeline options

Pipeline options allow to customize the execution of the models during the conversion pipeline.
This includes options for the OCR engines, the table model as well as enrichment options which
can be enabled with `do_xyz = True`.


This is an automatic generated API reference of the all the pipeline options available in Docling.


::: docling.datamodel.pipeline_options
    handler: python
    options:
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        signature_crossrefs: true
        summary: true

<!-- ::: docling.document_converter.DocumentConverter
    handler: python
    options:
        show_if_no_docstring: true
        show_submodules: true -->
        


---

# Docling Document

With Docling v2, we introduced a unified document representation format called `DoclingDocument`. It is defined as a
pydantic datatype, which can express several features common to documents, such as:

* Text, Tables, Pictures, and more
* Document hierarchy with sections and groups
* Disambiguation between main body and headers, footers (furniture)
* Layout information (i.e. bounding boxes) for all items, if available
* Provenance information

The definition of the Pydantic types is implemented in the module `docling_core.types.doc`, more details in [source code definitions](https://github.com/docling-project/docling-core/tree/main/docling_core/types/doc).

It also brings a set of document construction APIs to build up a `DoclingDocument` from scratch.

## Example document structures

To illustrate the features of the `DoclingDocument` format, in the subsections below we consider the
`DoclingDocument` converted from `tests/data/word_sample.docx` and we present some side-by-side comparisons,
where the left side shows snippets from the converted document
serialized as YAML and the right one shows the corresponding parts of the original MS Word.

### Basic structure

A `DoclingDocument` exposes top-level fields for the document content, organized in two categories.
The first category is the _content items_, which are stored in these fields:

- `texts`: All items that have a text representation (paragraph, section heading, equation, ...). Base class is `TextItem`.
- `tables`: All tables, type `TableItem`. Can carry structure annotations.
- `pictures`: All pictures, type `PictureItem`. Can carry structure annotations.
- `key_value_items`: All key-value items.

All of the above fields are lists and store items inheriting from the `DocItem` type. They can express different
data structures depending on their type, and reference parents and children through JSON pointers.

The second category is _content structure_, which is encapsulated in:

- `body`: The root node of a tree-structure for the main document body
- `furniture`: The root node of a tree-structure for all items that don't belong into the body (headers, footers, ...)
- `groups`: A set of items that don't represent content, but act as containers for other content items (e.g. a list, a chapter)

All of the above fields are only storing `NodeItem` instances, which reference children and parents
through JSON pointers.

The reading order of the document is encapsulated through the `body` tree and the order of _children_ in each item
in the tree.

Below example shows how all items in the first page are nested below the `title` item (`#/texts/1`).

![doc_hierarchy_1](../assets/docling_doc_hierarchy_1.png)

### Grouping

Below example shows how all items under the heading "Let's swim" (`#/texts/5`) are nested as children. The children of
"Let's swim" are both text items and groups, which contain the list elements. The group items are stored in the
top-level `groups` field.

![doc_hierarchy_2](../assets/docling_doc_hierarchy_2.png)

<!--
### Tables

TBD

### Pictures

TBD

### Provenance

TBD
 -->


---

# Index

In this space, you can peek under the hood and learn some fundamental Docling concepts!

Here some of our picks to get you started:

- 🏛️ Docling [architecture](./architecture.md)
- 📄 [Docling Document](./docling_document.md)
- core operations like ✍️ [serialization](./serialization.md) and ✂️ [chunking](./chunking.md)

👈 ... and there is much more: explore all the concepts using the navigation menu on the side

<div class="grid" style="text-align: center">
    <div class="card">
        <img loading="lazy" alt="Docling architecture" src="../assets/docling_arch.png" width="75%" />
        <hr />
        Docling architecture outline
    </div>
</div>


---

# Architecture

![docling_architecture](../assets/docling_arch.png)

In a nutshell, Docling's architecture is outlined in the diagram above.

For each document format, the *document converter* knows which format-specific *backend* to employ for parsing the document and which *pipeline* to use for orchestrating the execution, along with any relevant *options*.

!!! tip

    While the document converter holds a default mapping, this configuration is parametrizable, so e.g. for the PDF format, different backends and different pipeline options can be used — see [Usage](../usage/index.md#adjust-pipeline-features).

The *conversion result* contains the [*Docling document*](./docling_document.md), Docling's fundamental document representation.

Some typical scenarios for using a Docling document include directly calling its *export methods*, such as for markdown, dictionary etc., or having it serialized by a
[*serializer*](./serialization.md) or chunked by a [*chunker*](./chunking.md).

For more details on Docling's architecture, check out the [Docling Technical Report](https://arxiv.org/abs/2408.09869).

!!! note

    The components illustrated with dashed outline indicate base classes that can be subclassed for specialized implementations.


---

# Confidence Scores

## Introduction

**Confidence grades** were introduced in [v2.34.0](https://github.com/docling-project/docling/releases/tag/v2.34.0) to help users understand how well a conversion performed and guide decisions about post-processing workflows. They are available in the [`confidence`](../../reference/document_converter/#docling.document_converter.ConversionResult.confidence) field of the [[`ConversionResult`](https://github.com/docling-project/docling/blob/main/docling/datamodel/document.py#L417)](../../reference/document_converter/#docling.document_converter.ConversionResult) object returned by the document converter.

## Purpose

Complex layouts, poor scan quality, or challenging formatting can lead to suboptimal document conversion results that may require additional attention or alternative conversion pipelines.

Confidence scores provide a quantitative assessment of document conversion quality. Each confidence report includes a **numerical score** (0.0 to 1.0) measuring conversion accuracy, and a **quality grade** (poor, fair, good, excellent) for quick interpretation.

!!! note "Focus on quality grades!"

    Users can and should safely focus on the document-level grade fields — `mean_grade` and `low_grade` — to assess overall conversion quality. Numerical scores are used internally and are for informational purposes only; their computation and weighting may change in the future.

Use cases for confidence grades include:

- Identify documents requiring manual review after the conversion
- Adjust conversion pipelines to the most appropriate for each document type
- Set confidence thresholds for unattended batch conversions
- Catch potential conversion issues early in your workflow.

## Concepts

### Scores and grades

A confidence report contains *scores* and *grades*:

- **Scores**: Numerical values between 0.0 and 1.0, where higher values indicate better conversion quality, for internal use only
- **Grades**: Categorical quality assessments based on score thresholds, used to assess the overall conversion confidence:
  - `POOR`
  - `FAIR`
  - `GOOD`
  - `EXCELLENT`

### Types of confidence calculated

Each confidence report includes four component scores and grades:

- **`layout_score`**: Overall quality of document element recognition 
- **`ocr_score`**: Quality of OCR-extracted content
- **`parse_score`**: 10th percentile score of digital text cells (emphasizes problem areas)
- **`table_score`**: Table extraction quality *(not yet implemented)*

### Summary grades

Two aggregate grades provide overall document quality assessment:

- **`mean_grade`**: Average of the four component scores
- **`low_grade`**: 5th percentile score (highlights worst-performing areas)

### Page-level vs document-level

Confidence grades are calculated at two levels:

- **Page-level**: Individual scores and grades for each page, stored in the `pages` field
- **Document-level**: Overall scores and grades for the entire document, calculated as averages of the page-level grades and stored in fields equally named in the root [[`ConfidenceReport`](https://github.com/docling-project/docling/blob/main/docling/datamodel/base_models.py#L472)](h../../reference/document_converter/#docling.document_converter.ConversionResult.confidence)

### Example

![confidence_scores](../assets/confidence_scores.png)



---

## Source References

- [`ConversionResult`](https://github.com/docling-project/docling/blob/main/docling/datamodel/document.py#L417)
- [`ConfidenceReport`](https://github.com/docling-project/docling/blob/main/docling/datamodel/base_models.py#L472)


---

# Serialization

## Introduction

A *document serializer* (AKA simply *serializer*) is a Docling abstraction that is
initialized with a given [`DoclingDocument`](./docling_document.md) and returns a
textual representation for that document.

Besides the document serializer, Docling defines similar abstractions for several
document subcomponents, for example: *text serializer*, *table serializer*,
*picture serializer*, *list serializer*, *inline serializer*, and more.

Last but not least, a *serializer provider* is a wrapper that abstracts the
document serialization strategy from the document instance.

## Base classes

To enable both flexibility for downstream applications and out-of-the-box utility,
Docling defines a serialization class hierarchy, providing:

- base types for the above abstractions: `BaseDocSerializer`, as well as
  `BaseTextSerializer`, `BaseTableSerializer` etc, and `BaseSerializerProvider`, and
- specific subclasses for the above-mentioned base types, e.g. `MarkdownDocSerializer`.

You can review all methods required to define the above base classes [here](https://github.com/docling-project/docling-core/blob/main/docling_core/transforms/serializer/base.py).

From a client perspective, the most relevant is `BaseDocSerializer.serialize()`, which
returns the textual representation, as well as relevant metadata on which document
components contributed to that serialization.

## Use in `DoclingDocument` export methods

Docling provides predefined serializers for Markdown, HTML, and DocTags.

The respective `DoclingDocument` export methods (e.g. `export_to_markdown()`) are
provided as user shorthands — internally directly instantiating and delegating to
respective serializers.

## Examples

For an example showcasing how to use serializers, see
[here](../examples/serialization.ipynb).


---

# Factory registration

Docling allows to be extended with third-party plugins which extend the choice of options provided in several steps of the pipeline.

Plugins are loaded via the [pluggy](https://github.com/pytest-dev/pluggy/) system which allows third-party developers to register the new capabilities using the [setuptools entrypoint](https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins).

The actual entrypoint definition might vary, depending on the packaging system you are using. Here are a few examples:

=== "pyproject.toml"

    ```toml
    [project.entry-points."docling"]
    your_plugin_name = "your_package.module"
    ```

=== "poetry v1 pyproject.toml"

    ```toml
    [tool.poetry.plugins."docling"]
    your_plugin_name = "your_package.module"
    ```

=== "setup.cfg"

    ```ini
    [options.entry_points]
    docling =
        your_plugin_name = your_package.module
    ```

=== "setup.py"

    ```py
    from setuptools import setup

    setup(
        # ...,
        entry_points = {
            'docling': [
                'your_plugin_name = "your_package.module"'
            ]
        }
    )
    ```

- `your_plugin_name` is the name you choose for your plugin. This must be unique among the broader Docling ecosystem.
- `your_package.module` is the reference to the module in your package which is responsible for the plugin registration.

## Plugin factories

### OCR factory

The OCR factory allows to provide more OCR engines to the Docling users.

The content of `your_package.module` registers the OCR engines with a code similar to:

```py
# Factory registration
def ocr_engines():
    return {
        "ocr_engines": [
            YourOcrModel,
        ]
    }
```

where `YourOcrModel` must implement the [[`BaseOcrModel`](https://github.com/docling-project/docling/blob/main/docling/models/base_ocr_model.py#L24)](https://github.com/docling-project/docling/blob/main/docling/models/base_ocr_model.py#L23) and provide an options class derived from [[`OcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L79)](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L105).

If you look for an example, the [default Docling plugins](https://github.com/docling-project/docling/blob/main/docling/models/plugins/defaults.py) is a good starting point.

## Third-party plugins

When the plugin is not provided by the main `docling` package but by a third-party package this have to be enabled explicitly via the `allow_external_plugins` option.

```py
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.allow_external_plugins = True  # <-- enabled the external plugins
pipeline_options.ocr_options = YourOptions  # <-- your options here

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)
```

### Using the `docling` CLI

Similarly, when using the `docling` users have to enable external plugins before selecting the new one.

```sh
# Show the external plugins
docling --show-external-plugins

# Run docling with the new plugin
docling --allow-external-plugins --ocr-engine=NAME
```


---

## Source References

- [`BaseOcrModel`](https://github.com/docling-project/docling/blob/main/docling/models/base_ocr_model.py#L24)
- [`OcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L79) - OCR options.


---

# Chunking

## Introduction

!!! note "Chunking approaches"

    Starting from a `DoclingDocument`, there are in principle two possible chunking
    approaches:

    1. exporting the `DoclingDocument` to Markdown (or similar format) and then
      performing user-defined chunking as a post-processing step, or
    2. using native Docling chunkers, i.e. operating directly on the `DoclingDocument`

    This page is about the latter, i.e. using native Docling chunkers.
    For an example of using approach (1) check out e.g.
    [this recipe](../examples/rag_langchain.ipynb) looking at the Markdown export mode.

A *chunker* is a Docling abstraction that, given a
[`DoclingDocument`](./docling_document.md), returns a stream of chunks, each of which
captures some part of the document as a string accompanied by respective metadata.

To enable both flexibility for downstream applications and out-of-the-box utility,
Docling defines a chunker class hierarchy, providing a base type, `BaseChunker`, as well
as specific subclasses.

Docling integration with gen AI frameworks like LlamaIndex is done using the
`BaseChunker` interface, so users can easily plug in any built-in, self-defined, or
third-party `BaseChunker` implementation.

## Base Chunker

The `BaseChunker` base class API defines that any chunker should provide the following:

- `def chunk(self, dl_doc: DoclingDocument, **kwargs) -> Iterator[BaseChunk]`:
  Returning the chunks for the provided document.
- `def contextualize(self, chunk: BaseChunk) -> str`:
  Returning the potentially metadata-enriched serialization of the chunk, typically
  used to feed an embedding model (or generation model).

## Hybrid Chunker

!!! note "To access `HybridChunker`"

    - If you are using the `docling` package, you can import as follows:
        ```python
        from docling.chunking import HybridChunker
        ```
    - If you are only using the `docling-core` package, you must ensure to install
        the `chunking` extra if you want to use HuggingFace tokenizers, e.g.
        ```shell
        pip install 'docling-core[chunking]'
        ```
        or the `chunking-openai` extra if you prefer Open AI tokenizers (tiktoken), e.g.
        ```shell
        pip install 'docling-core[chunking-openai]'
        ```
        and then you
        can import as follows:
        ```python
        from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
        ```

The `HybridChunker` implementation uses a hybrid approach, applying tokenization-aware
refinements on top of document-based [hierarchical](#hierarchical-chunker) chunking.

More precisely:

- it starts from the result of the hierarchical chunker and, based on the user-provided
  tokenizer (typically to be aligned to the embedding model tokenizer), it:
- does one pass where it splits chunks only when needed (i.e. oversized w.r.t.
tokens), &
- another pass where it merges chunks only when possible (i.e. undersized successive
chunks with same headings & captions) — users can opt out of this step via param
`merge_peers` (by default `True`)

👉 Usage examples:

- [Hybrid chunking](../examples/hybrid_chunking.ipynb)
- [Advanced chunking & serialization](../examples/advanced_chunking_and_serialization.ipynb)

## Hierarchical Chunker

The `HierarchicalChunker` implementation uses the document structure information from
the [`DoclingDocument`](./docling_document.md) to create one chunk for each individual
detected document element, by default only merging together list items (can be opted out
via param `merge_list_items`). It also takes care of attaching all relevant document
metadata, including headers and captions.


---

