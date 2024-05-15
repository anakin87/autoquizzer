from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from haystack import Document, component, logging
from haystack.components.converters.utils import (
    get_bytestream_from_source,
    normalize_metadata,
)
from haystack.dataclasses import ByteStream

from trafilatura import extract

import json
import json_repair

logger = logging.getLogger(__name__)


@component
class TrafilaturaHTMLConverter:
    """
    Converts an HTML file to a Document using Trafilatura.

    Usage example:
    ```python
    converter = TrafilaturaHTMLConverter()
    results = converter.run(sources=["path/to/sample.html"])
    documents = results["documents"]
    print(documents[0].content)
    # 'This is a text from the HTML file.'
    ```
    """

    @component.output_types(documents=List[Document])
    def run(
        self,
        sources: List[Union[str, Path, ByteStream]],
        meta: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        """
        Converts a list of HTML files to Documents.

        :param sources:
            List of HTML file paths or ByteStream objects.
        :param meta:
            Optional metadata to attach to the Documents.
            This value can be either a list of dictionaries or a single dictionary.
            If it's a single dictionary, its content is added to the metadata of all produced Documents.
            If it's a list, the length of the list must match the number of sources, because the two lists will be zipped.
            If `sources` contains ByteStream objects, their `meta` will be added to the output Documents.
        :param extract_kwargs:
            Additional keyword arguments to pass to the Trafilatura `extract` method.
            See the [Trafilatura documentation](https://trafilatura.readthedocs.io/en/latest/usage-python.html) for more information.

        :returns:
            A dictionary with the following keys:
            - `documents`: Created Documents
        """

        documents = []
        meta_list = normalize_metadata(meta=meta, sources_count=len(sources))

        for source, metadata in zip(sources, meta_list):
            try:
                bytestream = get_bytestream_from_source(source=source)
            except Exception as e:
                logger.warning(
                    "Could not read {source}. Skipping it. Error: {error}",
                    source=source,
                    error=e,
                )
                continue

            text = None
            try:
                text = extract(bytestream.data.decode("utf-8"))
            except Exception as conversion_e:
                logger.warning(
                    "Failed to extract text from {source}. Error: {error}",
                    source=source,
                    error=conversion_e,
                )
                continue

            document = Document(content=text, meta={**bytestream.meta, **metadata})
            documents.append(document)

        return {"documents": documents}


@component
class QuizParser:
    @component.output_types(quiz=Dict)
    def run(self, replies: List[str]):
        reply = replies[0]

        # even if prompted to respond with JSON only, sometimes the model returns a mix of JSON and text
        first_index = min(reply.find("{"), reply.find("["))
        last_index = max(reply.rfind("}"), reply.rfind("]")) + 1

        json_portion = reply[first_index:last_index]

        try:
            quiz = json.loads(json_portion)
        except json.JSONDecodeError:
            # if the JSON is not well-formed, try to repair it
            quiz = json_repair.loads(json_portion)

        # sometimes the JSON contains a list instead of a dictionary
        if isinstance(quiz, list):
            quiz = quiz[0]

        print(quiz)

        return {"quiz": quiz}
