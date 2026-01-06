# Docling Source Symbol Catalog

Generated: 2026-01-06T01:29:16.730849

Total symbols: 495

## By File (96 files)

### `docling/backend/abstract_backend.py`

- Line 19: `AbstractDocumentBackend` (class)
- Line 54: `PaginatedDocumentBackend` (class)
- Line 66: `DeclarativeDocumentBackend` (class)

### `docling/backend/asciidoc_backend.py`

- Line 29: `AsciiDocBackend` (class)

### `docling/backend/csv_backend.py`

- Line 17: `CsvDocumentBackend` (class)

### `docling/backend/docling_parse_backend.py`

- Line 26: `DoclingParsePageBackend` (class)
- Line 200: `DoclingParseDocumentBackend` (class)

### `docling/backend/docling_parse_v2_backend.py`

- Line 32: `DoclingParseV2PageBackend` (class)
- Line 47: `DoclingParseV2PageBackend.is_valid` (method)
- Line 99: `DoclingParseV2PageBackend.get_text_in_rect` (method)
- Line 139: `DoclingParseV2PageBackend.get_segmented_page` (method)
- Line 159: `DoclingParseV2PageBackend.get_text_cells` (method)
- Line 162: `DoclingParseV2PageBackend.get_bitmap_rects` (method)
- Line 183: `DoclingParseV2PageBackend.get_page_image` (method)
- Line 219: `DoclingParseV2PageBackend.get_size` (method)
- Line 223: `DoclingParseV2PageBackend.unload` (method)
- Line 228: `DoclingParseV2DocumentBackend` (class)
- Line 251: `DoclingParseV2DocumentBackend.page_count` (method)
- Line 262: `DoclingParseV2DocumentBackend.load_page` (method)

### `docling/backend/docling_parse_v4_backend.py`

- Line 25: `DoclingParseV4PageBackend` (class)
- Line 192: `DoclingParseV4DocumentBackend` (class)

### `docling/backend/docx/drawingml/utils.py`

- Line 13: `get_libreoffice_cmd` (function)
- Line 44: `get_docx_to_pdf_converter` (function)
- Line 56: `convert_with_libreoffice` (function)
- Line 87: `crop_whitespace` (function)
- Line 106: `get_pil_from_dml_docx` (function)

### `docling/backend/docx/latex/omml.py`

- Line 47: `load` (function)
- Line 53: `load_string` (function)
- Line 59: `escape_latex` (function)
- Line 72: `get_val` (function)
- Line 79: `Tag2Method` (class)
- Line 80: `Tag2Method.call_method` (method)
- Line 90: `Tag2Method.process_children_list` (method)
- Line 107: `Tag2Method.process_children_dict` (method)
- Line 116: `Tag2Method.process_children` (method)
- Line 127: `Tag2Method.process_unknow` (method)
- Line 131: `Pr` (class)
- Line 153: `Pr.do_brk` (method)
- Line 157: `Pr.do_common` (method)
- Line 174: `oMath2Latex` (class)
- Line 206: `oMath2Latex.latex` (method)
- Line 209: `oMath2Latex.do_acc` (method)
- Line 219: `oMath2Latex.do_bar` (method)
- Line 228: `oMath2Latex.do_d` (method)
- Line 245: `oMath2Latex.do_spre` (method)
- Line 250: `oMath2Latex.do_sub` (method)
- Line 254: `oMath2Latex.do_sup` (method)
- Line 258: `oMath2Latex.do_f` (method)
- Line 275: `oMath2Latex.do_func` (method)
- Line 283: `oMath2Latex.do_fname` (method)
- Line 301: `oMath2Latex.do_groupchr` (method)
- Line 310: `oMath2Latex.do_rad` (method)
- Line 322: `oMath2Latex.do_eqarr` (method)
- Line 332: `oMath2Latex.do_limlow` (method)
- Line 343: `oMath2Latex.do_limupp` (method)
- Line 350: `oMath2Latex.do_lim` (method)
- Line 356: `oMath2Latex.do_m` (method)
- Line 368: `oMath2Latex.do_mr` (method)
- Line 376: `oMath2Latex.do_nary` (method)
- Line 390: `oMath2Latex.process_unicode` (method)
- Line 414: `oMath2Latex.do_r` (method)

### `docling/backend/html_backend.py`

- Line 127: `_Context` (class)
- Line 132: `AnnotatedText` (class)
- Line 139: `AnnotatedTextList` (class)
- Line 140: `AnnotatedTextList.to_single_text_element` (method)
- Line 172: `AnnotatedTextList.simplify_text_elements` (method)
- Line 211: `AnnotatedTextList.split_by_newline` (method)
- Line 230: `HTMLDocumentBackend` (class)
- Line 444: `HTMLDocumentBackend.group_cell_elements` (method)
- Line 466: `HTMLDocumentBackend.process_rich_table_cells` (method)
- Line 519: `HTMLDocumentBackend.parse_table_data` (method)
- Line 1159: `HTMLDocumentBackend.get_html_table_row_col` (method)
- Line 1289: `get_img_hyperlink` (function)
- Line 1399: `HTMLDocumentBackend.get_text` (method)

### `docling/backend/image_backend.py`

- Line 25: `_ImagePageBackend` (class)
- Line 121: `ImageDocumentBackend` (class)

### `docling/backend/json/docling_json_backend.py`

- Line 13: `DoclingJSONBackend` (class)

### `docling/backend/md_backend.py`

- Line 49: `_PendingCreationType` (class)
- Line 56: `_HeadingCreationPayload` (class)
- Line 61: `_ListItemCreationPayload` (class)
- Line 75: `MarkdownDocumentBackend` (class)
- Line 80: `replace_match` (function)
- Line 534: `MarkdownDocumentBackend.supports_pagination` (method)
- Line 538: `MarkdownDocumentBackend.supported_formats` (method)

### `docling/backend/mets_gbs_backend.py`

- Line 54: `MetsGbsPageBackend` (class)
- Line 143: `_UseType` (class)
- Line 150: `_FileInfo` (class)
- Line 158: `_PageFiles` (class)
- Line 197: `MetsGbsDocumentBackend` (class)

### `docling/backend/msexcel_backend.py`

- Line 43: `DataRegion` (class)
- Line 59: `DataRegion.width` (method)
- Line 63: `DataRegion.height` (method)
- Line 68: `ExcelCell` (class)
- Line 86: `ExcelTable` (class)
- Line 103: `MsExcelDocumentBackend` (class)

### `docling/backend/mspowerpoint_backend.py`

- Line 35: `MsPowerpointDocumentBackend` (class)
- Line 103: `MsPowerpointDocumentBackend.generate_prov` (method)
- Line 124: `MsPowerpointDocumentBackend.handle_text_elements` (method)
- Line 133: `is_list_item` (function)
- Line 212: `MsPowerpointDocumentBackend.handle_title` (method)
- Line 235: `MsPowerpointDocumentBackend.handle_pictures` (method)
- Line 256: `MsPowerpointDocumentBackend.handle_tables` (method)
- Line 320: `MsPowerpointDocumentBackend.walk_linear` (method)
- Line 340: `handle_shapes` (function)
- Line 367: `handle_groups` (function)

### `docling/backend/msword_backend.py`

- Line 50: `MsWordDocumentBackend` (class)
- Line 164: `MsWordDocumentBackend.load_msword_file` (method)
- Line 1518: `get_docx_image` (function)

### `docling/backend/noop_backend.py`

- Line 13: `NoOpBackend` (class)

### `docling/backend/pdf_backend.py`

- Line 17: `PdfPageBackend` (class)
- Line 53: `PdfDocumentBackend` (class)

### `docling/backend/pypdfium2_backend.py`

- Line 27: `get_pdf_page_geometry` (function)
- Line 102: `PyPdfiumPageBackend` (class)
- Line 158: `merge_horizontal_cells` (function)
- Line 166: `group_rows` (function)
- Line 197: `merge_row` (function)
- Line 221: `merge_group` (function)
- Line 373: `PyPdfiumDocumentBackend` (class)

### `docling/backend/webvtt_backend.py`

- Line 27: `_WebVTTTimestamp` (class)
- Line 52: `_WebVTTTimestamp.validate_raw` (method)
- Line 69: `_WebVTTTimestamp.seconds` (method)
- Line 88: `_WebVTTCueTimings` (class)
- Line 97: `_WebVTTCueTimings.check_order` (method)
- Line 108: `_WebVTTCueTextSpan` (class)
- Line 116: `_WebVTTCueTextSpan.validate_text` (method)
- Line 128: `_WebVTTCueVoiceSpan` (class)
- Line 151: `_WebVTTCueVoiceSpan.validate_annotation` (method)
- Line 162: `_WebVTTCueVoiceSpan.validate_classes` (method)
- Line 179: `_WebVTTCueClassSpan` (class)
- Line 189: `_WebVTTCueItalicSpan` (class)
- Line 199: `_WebVTTCueBoldSpan` (class)
- Line 209: `_WebVTTCueUnderlineSpan` (class)
- Line 232: `_WebVTTCueBlock` (class)
- Line 258: `_WebVTTCueBlock.validate_payload` (method)
- Line 265: `_WebVTTCueBlock.parse` (method)
- Line 378: `_WebVTTFile` (class)
- Line 384: `_WebVTTFile.verify_signature` (method)
- Line 432: `WebVTTDocumentBackend` (class)

### `docling/backend/xml/jats_backend.py`

- Line 36: `Abstract` (class)
- Line 41: `Author` (class)
- Line 46: `Citation` (class)
- Line 58: `Table` (class)
- Line 64: `XMLComponents` (class)
- Line 70: `JatsDocumentBackend` (class)

### `docling/backend/xml/uspto_backend.py`

- Line 43: `PatentHeading` (class)
- Line 60: `PatentUsptoDocumentBackend` (class)
- Line 152: `PatentUspto` (class)
- Line 167: `PatentUsptoIce` (class)
- Line 212: `PatentHandler` (class)
- Line 219: `Element` (class)
- Line 266: `PatentHandler.startElement` (method)
- Line 282: `PatentHandler.skippedEntity` (method)
- Line 316: `PatentHandler.endElement` (method)
- Line 330: `PatentHandler.characters` (method)
- Line 503: `PatentUsptoGrantV2` (class)
- Line 848: `PatentUsptoGrantAps` (class)
- Line 856: `Section` (class)
- Line 866: `Field` (class)
- Line 896: `PatentUsptoGrantAps.get_last_text_item` (method)
- Line 917: `PatentUsptoGrantAps.store_section` (method)
- Line 943: `PatentUsptoGrantAps.store_content` (method)
- Line 1063: `PatentUsptoAppV1` (class)
- Line 1400: `XmlTable` (class)
- Line 1407: `ColInfo` (class)
- Line 1411: `MinColInfoType` (class)
- Line 1415: `ColInfoType` (class)
- Line 1697: `HtmlEntity` (class)
- Line 1862: `HtmlEntity.get_superscript` (method)
- Line 1873: `HtmlEntity.get_subscript` (method)
- Line 1884: `HtmlEntity.get_math_italic` (method)
- Line 1895: `HtmlEntity.get_greek_from_iso8879` (method)

### `docling/cli/main.py`

- Line 171: `logo_callback` (function)
- Line 177: `version_callback` (function)
- Line 189: `show_external_plugins_callback` (function)
- Line 195: `print_external_plugins` (function)
- Line 216: `export_documents` (function)

### `docling/cli/models.py`

- Line 30: `_AvailableModels` (class)
- Line 55: `download` (function)
- Line 139: `download_hf_repo` (function)

### `docling/datamodel/accelerator_options.py`

- Line 13: `AcceleratorDevice` (class)
- Line 23: `AcceleratorOptions` (class)
- Line 33: `AcceleratorOptions.validate_device` (method)
- Line 45: `AcceleratorOptions.check_alternative_envvars` (method)

### `docling/datamodel/asr_model_specs.py`

- Line 471: `AsrModelType` (class)

### `docling/datamodel/backend_options.py`

- Line 7: `BaseBackendOptions` (class)
- Line 18: `DeclarativeBackendOptions` (class)
- Line 24: `HTMLBackendOptions` (class)
- Line 53: `MarkdownBackendOptions` (class)
- Line 73: `PdfBackendOptions` (class)
- Line 80: `MsExcelBackendOptions` (class)

### `docling/datamodel/base_models.py`

- Line 37: `BaseFormatOption` (class)
- Line 46: `ConversionStatus` (class)
- Line 55: `InputFormat` (class)
- Line 75: `OutputFormat` (class)
- Line 159: `DocInputType` (class)
- Line 164: `DoclingComponentType` (class)
- Line 172: `VlmStopReason` (class)
- Line 179: `ErrorItem` (class)
- Line 185: `Cluster` (class)
- Line 198: `BasePageElement` (class)
- Line 206: `LayoutPrediction` (class)
- Line 210: `VlmPredictionToken` (class)
- Line 216: `VlmPrediction` (class)
- Line 225: `ContainerElement` (class)
- Line 238: `TableStructurePrediction` (class)
- Line 242: `TextElement` (class)
- Line 246: `FigureElement` (class)
- Line 263: `FigureClassificationPrediction` (class)
- Line 268: `EquationPrediction` (class)
- Line 273: `PagePredictions` (class)
- Line 284: `AssembledUnit` (class)
- Line 290: `ItemAndImageEnrichmentElement` (class)
- Line 297: `Page` (class)
- Line 316: `Page.cells` (method)
- Line 323: `Page.get_image` (method)
- Line 354: `Page.image` (method)
- Line 361: `OpenAiChatMessage` (class)
- Line 366: `OpenAiResponseChoice` (class)
- Line 372: `OpenAiResponseUsage` (class)
- Line 378: `OpenAiApiResponse` (class)
- Line 394: `QualityGrade` (class)
- Line 402: `PageConfidenceScores` (class)
- Line 434: `PageConfidenceScores.mean_grade` (method)
- Line 439: `PageConfidenceScores.low_grade` (method)
- Line 444: `PageConfidenceScores.mean_score` (method)
- Line 458: `PageConfidenceScores.low_score` (method)
- Line 472: `ConfidenceReport` (class)

### `docling/datamodel/document.py`

- Line 111: `InputDocument` (class)
- Line 227: `DocumentFormat` (class)
- Line 232: `DoclingVersion` (class)
- Line 242: `ConversionAssets` (class)
- Line 258: `ConversionAssets.legacy_document` (method)
- Line 261: `ConversionAssets.save` (method)
- Line 273: `to_jsonable` (function)
- Line 302: `write_json` (function)
- Line 351: `read_json` (function)
- Line 417: `ConversionResult` (class)
- Line 422: `_DummyBackend` (class)
- Line 441: `_DocumentConversionInput` (class)
- Line 446: `_DocumentConversionInput.docs` (method)

### `docling/datamodel/extraction.py`

- Line 11: `ExtractedPageData` (class)
- Line 25: `ExtractionResult` (class)

### `docling/datamodel/layout_model_specs.py`

- Line 13: `LayoutModelConfig` (class)
- Line 26: `LayoutModelConfig.model_repo_folder` (method)
- Line 84: `LayoutModelType` (class)

### `docling/datamodel/pipeline_options.py`

- Line 49: `BaseOptions` (class)
- Line 55: `TableFormerMode` (class)
- Line 62: `BaseTableStructureOptions` (class)
- Line 66: `TableStructureOptions` (class)
- Line 79: `OcrOptions` (class)
- Line 107: `OcrAutoOptions` (class)
- Line 119: `RapidOcrOptions` (class)
- Line 163: `EasyOcrOptions` (class)
- Line 185: `TesseractCliOcrOptions` (class)
- Line 201: `TesseractOcrOptions` (class)
- Line 216: `OcrMacOptions` (class)
- Line 229: `PictureDescriptionBaseOptions` (class)
- Line 238: `PictureDescriptionApiOptions` (class)
- Line 251: `PictureDescriptionVlmOptions` (class)
- Line 260: `PictureDescriptionVlmOptions.repo_cache_folder` (method)
- Line 277: `PdfBackend` (class)
- Line 290: `OcrEngine` (class)
- Line 301: `PipelineOptions` (class)
- Line 344: `ConvertPipelineOptions` (class)
- Line 355: `PaginatedPipelineOptions` (class)
- Line 361: `VlmPipelineOptions` (class)
- Line 372: `BaseLayoutOptions` (class)
- Line 383: `LayoutOptions` (class)
- Line 391: `AsrPipelineOptions` (class)
- Line 395: `VlmExtractionPipelineOptions` (class)
- Line 401: `PdfPipelineOptions` (class)
- Line 445: `ProcessingPipeline` (class)
- Line 452: `ThreadedPdfPipelineOptions` (class)

### `docling/datamodel/pipeline_options_asr_model.py`

- Line 14: `BaseAsrOptions` (class)
- Line 19: `InferenceAsrFramework` (class)
- Line 25: `InlineAsrOptions` (class)
- Line 50: `InlineAsrNativeWhisperOptions` (class)
- Line 61: `InlineAsrMlxWhisperOptions` (class)

### `docling/datamodel/pipeline_options_vlm_model.py`

- Line 18: `BaseVlmOptions` (class)
- Line 43: `BaseVlmOptions.decode_response` (method)
- Line 47: `ResponseFormat` (class)
- Line 55: `InferenceFramework` (class)
- Line 61: `TransformersModelType` (class)
- Line 68: `TransformersPromptStyle` (class)
- Line 74: `InlineVlmOptions` (class)
- Line 115: `HuggingFaceVlmOptions` (class)
- Line 119: `ApiVlmOptions` (class)

### `docling/datamodel/settings.py`

- Line 22: `DocumentLimits` (class)
- Line 28: `BatchConcurrencySettings` (class)
- Line 40: `DebugSettings` (class)
- Line 53: `AppSettings` (class)

### `docling/datamodel/vlm_model_specs.py`

- Line 340: `VlmModelType` (class)

### `docling/document_converter.py`

- Line 73: `FormatOption` (class)
- Line 78: `FormatOption.set_optional_field_default` (method)
- Line 85: `CsvFormatOption` (class)
- Line 90: `ExcelFormatOption` (class)
- Line 95: `WordFormatOption` (class)
- Line 100: `PowerpointFormatOption` (class)
- Line 105: `MarkdownFormatOption` (class)
- Line 111: `AsciiDocFormatOption` (class)
- Line 116: `HTMLFormatOption` (class)
- Line 122: `PatentUsptoFormatOption` (class)
- Line 127: `XMLJatsFormatOption` (class)
- Line 132: `ImageFormatOption` (class)
- Line 137: `PdfFormatOption` (class)
- Line 143: `AudioFormatOption` (class)
- Line 178: `DocumentConverter` (class)
- Line 263: `DocumentConverter.initialize_pipeline` (method)
- Line 284: `DocumentConverter.convert` (method)
- Line 328: `DocumentConverter.convert_all` (method)
- Line 392: `DocumentConverter.convert_string` (method)

### `docling/document_extractor.py`

- Line 48: `ExtractionFormatOption` (class)
- Line 90: `DocumentExtractor` (class)
- Line 126: `DocumentExtractor.extract` (method)
- Line 148: `DocumentExtractor.extract_all` (method)

### `docling/exceptions.py`

- Line 1: `BaseError` (class)
- Line 5: `ConversionError` (class)
- Line 9: `OperationNotAllowed` (class)

### `docling/experimental/datamodel/table_crops_layout_options.py`

- Line 10: `TableCropsLayoutOptions` (class)

### `docling/experimental/datamodel/threaded_layout_vlm_pipeline_options.py`

- Line 17: `ThreadedLayoutVlmPipelineOptions` (class)
- Line 37: `ThreadedLayoutVlmPipelineOptions.validate_response_format` (method)

### `docling/experimental/models/table_crops_layout_model.py`

- Line 24: `TableCropsLayoutModel` (class)

### `docling/experimental/pipeline/threaded_layout_vlm_pipeline.py`

- Line 55: `ThreadedLayoutVlmPipeline` (class)
- Line 84: `LayoutAwareVlmOptions` (class)
- Line 85: `LayoutAwareVlmOptions.build_prompt` (method)

### `docling/models/api_vlm_model.py`

- Line 21: `ApiVlmModel` (class)
- Line 97: `ApiVlmModel.process_images` (method)

### `docling/models/auto_ocr_model.py`

- Line 25: `OcrAutoModel` (class)

### `docling/models/base_layout_model.py`

- Line 13: `BaseLayoutModel` (class)
- Line 22: `BaseLayoutModel.predict_layout` (method)

### `docling/models/base_model.py`

- Line 31: `BaseModelWithOptions` (class)
- Line 38: `BasePageModel` (class)
- Line 46: `BaseVlmModel` (class)
- Line 68: `BaseVlmPageModel` (class)
- Line 103: `BaseVlmPageModel.formulate_prompt` (method)
- Line 150: `GenericEnrichmentModel` (class)
- Line 158: `GenericEnrichmentModel.prepare_element` (method)
- Line 170: `BaseEnrichmentModel` (class)
- Line 179: `BaseItemAndImageEnrichmentModel` (class)

### `docling/models/base_ocr_model.py`

- Line 24: `BaseOcrModel` (class)
- Line 40: `BaseOcrModel.get_ocr_rects` (method)
- Line 46: `find_ocr_rects` (function)
- Line 125: `is_overlapping_with_existing_cells` (function)
- Line 140: `BaseOcrModel.post_process_cells` (method)
- Line 187: `BaseOcrModel.draw_ocr_rects_and_cells` (method)

### `docling/models/base_table_model.py`

- Line 13: `BaseTableStructureModel` (class)

### `docling/models/code_formula_model.py`

- Line 25: `CodeFormulaModelOptions` (class)
- Line 44: `CodeFormulaModel` (class)
- Line 270: `clean_text` (function)

### `docling/models/document_picture_classifier.py`

- Line 23: `DocumentPictureClassifierOptions` (class)
- Line 36: `DocumentPictureClassifier` (class)
- Line 118: `DocumentPictureClassifier.is_processable` (method)

### `docling/models/easyocr_model.py`

- Line 28: `EasyOcrModel` (class)

### `docling/models/factories/__init__.py`

- Line 15: `get_ocr_factory` (function)
- Line 23: `get_picture_description_factory` (function)
- Line 33: `get_layout_factory` (function)
- Line 41: `get_table_structure_factory` (function)

### `docling/models/factories/base_factory.py`

- Line 18: `FactoryMeta` (class)
- Line 24: `BaseFactory` (class)
- Line 35: `BaseFactory.registered_kind` (method)
- Line 38: `BaseFactory.get_enum` (method)
- Line 47: `BaseFactory.classes` (method)
- Line 51: `BaseFactory.registered_meta` (method)
- Line 54: `BaseFactory.create_instance` (method)
- Line 61: `BaseFactory.create_options` (method)
- Line 77: `BaseFactory.register` (method)
- Line 90: `BaseFactory.load_from_plugins` (method)
- Line 117: `BaseFactory.process_plugin` (method)

### `docling/models/factories/layout_factory.py`

- Line 5: `LayoutFactory` (class)

### `docling/models/factories/ocr_factory.py`

- Line 9: `OcrFactory` (class)

### `docling/models/factories/picture_description_factory.py`

- Line 9: `PictureDescriptionFactory` (class)

### `docling/models/factories/table_factory.py`

- Line 5: `TableStructureFactory` (class)

### `docling/models/layout_model.py`

- Line 28: `LayoutModel` (class)
- Line 108: `LayoutModel.draw_clusters_and_cells_side_by_side` (method)

### `docling/models/ocr_mac_model.py`

- Line 25: `OcrMacModel` (class)

### `docling/models/page_assemble_model.py`

- Line 26: `PageAssembleOptions` (class)
- Line 30: `PageAssembleModel` (class)
- Line 34: `PageAssembleModel.sanitize_text` (method)

### `docling/models/page_preprocessing_model.py`

- Line 18: `PagePreprocessingOptions` (class)
- Line 25: `PagePreprocessingModel` (class)
- Line 92: `draw_text_boxes` (function)
- Line 120: `PagePreprocessingModel.rate_text_quality` (method)

### `docling/models/picture_description_api_model.py`

- Line 18: `PictureDescriptionApiModel` (class)

### `docling/models/picture_description_base_model.py`

- Line 27: `PictureDescriptionBaseModel` (class)

### `docling/models/picture_description_vlm_model.py`

- Line 24: `PictureDescriptionVlmModel` (class)

### `docling/models/plugins/defaults.py`

- Line 1: `ocr_engines` (function)
- Line 21: `picture_description` (function)
- Line 33: `layout_engines` (function)
- Line 47: `table_structure_engines` (function)

### `docling/models/rapid_ocr_model.py`

- Line 31: `_ModelPathDetail` (class)
- Line 36: `RapidOcrModel` (class)
- Line 226: `RapidOcrModel.download_models` (method)
- Line 327: `RapidOcrModel.get_options_type` (method)

### `docling/models/readingorder_model.py`

- Line 36: `ReadingOrderOptions` (class)
- Line 42: `ReadingOrderModel` (class)

### `docling/models/table_structure_model.py`

- Line 29: `TableStructureModel` (class)
- Line 107: `TableStructureModel.draw_table_and_cells` (method)
- Line 174: `TableStructureModel.predict_tables` (method)

### `docling/models/tesseract_ocr_cli_model.py`

- Line 35: `TesseractOcrCliModel` (class)

### `docling/models/tesseract_ocr_model.py`

- Line 29: `TesseractOcrModel` (class)

### `docling/models/utils/generation_utils.py`

- Line 12: `GenerationStopper` (class)
- Line 20: `GenerationStopper.should_stop` (method)
- Line 23: `GenerationStopper.lookback_tokens` (method)
- Line 27: `DocTagsRepetitionStopper` (class)
- Line 78: `run_repetitive` (function)
- Line 119: `HFStoppingCriteriaWrapper` (class)

### `docling/models/utils/hf_model_download.py`

- Line 8: `download_hf_model` (function)
- Line 30: `HuggingFaceModelDownloadMixin` (class)

### `docling/models/vlm_models_inline/hf_transformers_model.py`

- Line 37: `HuggingFaceTransformersVlmModel` (class)

### `docling/models/vlm_models_inline/mlx_model.py`

- Line 38: `HuggingFaceMlxModel` (class)

### `docling/models/vlm_models_inline/nuextract_transformers_model.py`

- Line 27: `process_all_vision_info` (function)
- Line 52: `extract_example_images` (function)
- Line 108: `NuExtractTransformersModel` (class)

### `docling/models/vlm_models_inline/vllm_model.py`

- Line 31: `VllmVlmModel` (class)

### `docling/pipeline/asr_pipeline.py`

- Line 52: `_ConversationWord` (class)
- Line 62: `_ConversationItem` (class)
- Line 88: `_ConversationItem.to_string` (method)
- Line 101: `_NativeWhisperModel` (class)
- Line 158: `_NativeWhisperModel.run` (method)
- Line 214: `_NativeWhisperModel.transcribe` (method)
- Line 239: `_MlxWhisperModel` (class)
- Line 363: `AsrPipeline` (class)

### `docling/pipeline/base_extraction_pipeline.py`

- Line 15: `BaseExtractionPipeline` (class)
- Line 31: `BaseExtractionPipeline.execute` (method)
- Line 71: `BaseExtractionPipeline.get_default_options` (method)

### `docling/pipeline/base_pipeline.py`

- Line 43: `BasePipeline` (class)
- Line 138: `BasePipeline.is_backend_supported` (method)
- Line 142: `ConvertPipeline` (class)
- Line 191: `PaginatedPipeline` (class)
- Line 325: `PaginatedPipeline.initialize_page` (method)

### `docling/pipeline/extraction_vlm_pipeline.py`

- Line 32: `ExtractionVlmPipeline` (class)
- Line 194: `ExtractionTemplateFactory` (class)

### `docling/pipeline/legacy_standard_pdf_pipeline.py`

- Line 36: `LegacyStandardPdfPipeline` (class)
- Line 112: `LegacyStandardPdfPipeline.download_models_hf` (method)
- Line 126: `LegacyStandardPdfPipeline.get_ocr_model` (method)

### `docling/pipeline/simple_pipeline.py`

- Line 16: `SimplePipeline` (class)

### `docling/pipeline/standard_pdf_pipeline.py`

- Line 67: `ThreadedItem` (class)
- Line 79: `ProcessingResult` (class)
- Line 87: `ProcessingResult.success_count` (method)
- Line 91: `ProcessingResult.failure_count` (method)
- Line 95: `ProcessingResult.is_partial_success` (method)
- Line 99: `ProcessingResult.is_complete_failure` (method)
- Line 103: `ThreadedQueue` (class)
- Line 117: `ThreadedQueue.put` (method)
- Line 138: `ThreadedQueue.get_batch` (method)
- Line 160: `ThreadedQueue.close` (method)
- Line 168: `ThreadedQueue.closed` (method)
- Line 172: `ThreadedPipelineStage` (class)
- Line 200: `ThreadedPipelineStage.add_output_queue` (method)
- Line 204: `ThreadedPipelineStage.start` (method)
- Line 213: `ThreadedPipelineStage.stop` (method)
- Line 314: `PreprocessThreadedStage` (class)
- Line 399: `RunContext` (class)
- Line 413: `StandardPdfPipeline` (class)

### `docling/pipeline/threaded_standard_pdf_pipeline.py`

- Line 4: `ThreadedStandardPdfPipeline` (class)

### `docling/pipeline/vlm_pipeline.py`

- Line 51: `VlmPipeline` (class)
- Line 129: `VlmPipeline.extract_text_from_backend` (method)

### `docling/utils/accelerator_utils.py`

- Line 9: `decide_device` (function)

### `docling/utils/api_image_request.py`

- Line 17: `api_image_request` (function)
- Line 94: `api_image_request_streaming` (function)

### `docling/utils/export.py`

- Line 13: `generate_multimodal_pages` (function)

### `docling/utils/glm_utils.py`

- Line 21: `resolve_item` (function)
- Line 70: `to_docling_document` (function)

### `docling/utils/layout_postprocessor.py`

- Line 16: `UnionFind` (class)
- Line 23: `UnionFind.find` (method)
- Line 28: `UnionFind.union` (method)
- Line 41: `UnionFind.get_groups` (method)
- Line 49: `SpatialClusterIndex` (class)
- Line 63: `SpatialClusterIndex.add_cluster` (method)
- Line 70: `SpatialClusterIndex.remove_cluster` (method)
- Line 74: `SpatialClusterIndex.find_candidates` (method)
- Line 85: `SpatialClusterIndex.check_overlap` (method)
- Line 107: `Interval` (class)
- Line 121: `IntervalTree` (class)
- Line 127: `IntervalTree.insert` (method)
- Line 131: `IntervalTree.find_containing` (method)
- Line 154: `LayoutPostprocessor` (class)
- Line 221: `LayoutPostprocessor.postprocess` (method)

### `docling/utils/ocr_utils.py`

- Line 9: `map_tesseract_script` (function)
- Line 20: `parse_tesseract_orientation` (function)
- Line 35: `tesseract_box_to_bounding_rectangle` (function)

### `docling/utils/orientation.py`

- Line 9: `rotate_bounding_box` (function)

### `docling/utils/profiling.py`

- Line 15: `ProfilingScope` (class)
- Line 20: `ProfilingItem` (class)
- Line 26: `ProfilingItem.total` (method)
- Line 29: `ProfilingItem.avg` (method)
- Line 32: `ProfilingItem.std` (method)
- Line 35: `ProfilingItem.mean` (method)
- Line 38: `ProfilingItem.percentile` (method)
- Line 42: `TimeRecorder` (class)

### `docling/utils/utils.py`

- Line 11: `chunkify` (function)
- Line 19: `create_file_hash` (function)
- Line 40: `create_hash` (function)
- Line 47: `download_url_with_progress` (function)

### `docling/utils/visualization.py`

- Line 8: `draw_clusters` (function)

