from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from formhtr.libs.services.amazon_vision import AmazonVision
from formhtr.libs.services.azure_vision import AzureVision, OperationStatusCodes
from formhtr.libs.services.call_services import call_services
from formhtr.libs.services.google_vision import GoogleVision


def _google_word(content: str, coords: list[float]):
    x1, y1, x2, y2 = coords
    vertices = [
        SimpleNamespace(x=int(x1), y=int(y1)),
        SimpleNamespace(x=int(x2), y=int(y1)),
        SimpleNamespace(x=int(x2), y=int(y2)),
        SimpleNamespace(x=int(x1), y=int(y2)),
    ]
    return SimpleNamespace(
        description=content,
        bounding_poly=SimpleNamespace(vertices=vertices),
    )


def _azure_word(content: str, coords: list[float]):
    x1, y1, x2, y2 = [int(v) for v in coords]
    bbox = [x1, y1, x2, y1, x2, y2, x1, y2]
    return SimpleNamespace(text=content, bounding_box=bbox)


def test_google_process_output_normalizes_words(extracted_data):
    sample = extracted_data["ctd_front"]["google"][:3]
    outputs = [SimpleNamespace(description="full", bounding_poly=SimpleNamespace(vertices=[]))]
    outputs.extend(_google_word(item["content"], item["coords"]) for item in sample)

    google = GoogleVision.__new__(GoogleVision)
    normalized = google.process_output(outputs)

    assert len(normalized) == 3
    assert normalized[0].content == sample[0]["content"]
    assert normalized[0].get_coords() == sample[0]["coords"]


def test_amazon_process_output_maps_relative_to_absolute(extracted_data):
    sample = extracted_data["ctd_front"]["amazon"][:3]
    img_width, img_height = 2500, 3500

    blocks = []
    for item in sample:
        x1, y1, x2, y2 = item["coords"]
        blocks.append(
            {
                "BlockType": "WORD",
                "Text": item["content"],
                "Geometry": {
                    "BoundingBox": {
                        "Left": x1 / img_width,
                        "Top": y1 / img_height,
                        "Width": (x2 - x1) / img_width,
                        "Height": (y2 - y1) / img_height,
                    }
                },
            }
        )

    amazon = AmazonVision.__new__(AmazonVision)
    normalized = amazon.process_output({"Blocks": blocks}, img_width, img_height)

    assert len(normalized) == 3
    assert normalized[1].content == sample[1]["content"]
    assert normalized[1].start_x == sample[1]["coords"][0]
    assert normalized[1].end_y == sample[1]["coords"][3]


def test_azure_process_output_maps_words_when_succeeded(extracted_data):
    sample = extracted_data["ctd_front"]["azure"][:2]
    words = [_azure_word(item["content"], item["coords"]) for item in sample]
    outputs = SimpleNamespace(
        status=OperationStatusCodes.succeeded,
        analyze_result=SimpleNamespace(
            read_results=[SimpleNamespace(lines=[SimpleNamespace(words=words)])]
        ),
    )

    azure = AzureVision.__new__(AzureVision)
    normalized = azure.process_output(outputs)

    assert len(normalized) == 2
    assert normalized[0].content == sample[0]["content"]
    assert normalized[0].get_coords() == [int(v) for v in sample[0]["coords"]]


def test_call_services_uses_only_enabled_providers(monkeypatch):
    calls = {"google": 0, "amazon": 0, "azure": 0}

    class FakeGoogle:
        def __init__(self, _credentials):
            pass

        def annotate_image(self, image_stream):
            calls["google"] += 1
            assert image_stream.getvalue()
            return "google_raw"

        def process_output(self, outputs):
            return [f"google:{outputs}"]

    class FakeAmazon:
        def __init__(self, _credentials):
            pass

        def annotate_image(self, image_stream):
            calls["amazon"] += 1
            assert image_stream.getvalue()
            return "amazon_raw"

        def process_output(self, outputs, width, height):
            assert width == 12 and height == 10
            return [f"amazon:{outputs}"]

    class FakeAzure:
        def __init__(self, _credentials):
            pass

        def annotate_image(self, image_stream):
            calls["azure"] += 1
            assert image_stream.getvalue()
            return "azure_raw"

        def process_output(self, outputs):
            return [f"azure:{outputs}"]

    monkeypatch.setattr("formhtr.libs.services.call_services.GoogleVision", FakeGoogle)
    monkeypatch.setattr("formhtr.libs.services.call_services.AmazonVision", FakeAmazon)
    monkeypatch.setattr("formhtr.libs.services.call_services.AzureVision", FakeAzure)

    image = np.zeros((10, 12, 3), dtype=np.uint8)
    config = SimpleNamespace(width=12, height=10)

    out = call_services(
        image,
        credentials={"google": "g.json", "amazon": {"k": "v"}, "azure": None},
        config=config,
    )

    assert out["google"] == ["google:google_raw"]
    assert out["amazon"] == ["amazon:amazon_raw"]
    assert out["azure"] is None
    assert calls == {"google": 1, "amazon": 1, "azure": 0}
