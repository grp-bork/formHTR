from __future__ import annotations

import json

import pytest

from formhtr import cli


def test_process_logsheet_requires_at_least_one_ocr_credential(monkeypatch):
    monkeypatch.setattr(
        "formhtr.commands.process_logsheet.ensure_system_dependencies",
        lambda *_args, **_kwargs: None,
    )
    with pytest.raises(SystemExit):
        cli.main(
            [
                "process-logsheet",
                "--pdf-logsheet",
                "scan.pdf",
                "--pdf-template",
                "template.pdf",
                "--config-file",
                "config.json",
                "--output-file",
                "out.xlsx",
            ]
        )


def test_process_logsheet_dispatches_and_prints_ratio(monkeypatch, capsys):
    monkeypatch.setattr(
        "formhtr.commands.process_logsheet.ensure_system_dependencies",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "formhtr.commands.process_logsheet.load_credentials",
        lambda **_kwargs: "CREDENTIALS",
    )
    captured = {}

    def fake_process(**kwargs):
        captured.update(kwargs)
        return {"ratio": 0.875}

    monkeypatch.setattr("formhtr.commands.process_logsheet.process_logsheet_to_xlsx", fake_process)

    code = cli.main(
        [
            "process-logsheet",
            "--pdf-logsheet",
            "scan.pdf",
            "--pdf-template",
            "template.pdf",
            "--config-file",
            "config.json",
            "--output-file",
            "out.xlsx",
            "--google",
            "google.json",
        ]
    )

    out = capsys.readouterr().out
    assert code == 0
    assert "Success ratio: 0.875" in out
    assert captured["credentials"] == "CREDENTIALS"
    assert captured["scanned_logsheet_pdf"] == "scan.pdf"
    assert captured["template_pdf"] == "template.pdf"


def test_select_rois_rejects_invalid_headless_display_combo():
    with pytest.raises(SystemExit):
        cli.main(
            [
                "select-rois",
                "--pdf-file",
                "template.pdf",
                "--output-file",
                "config.json",
                "--headless",
                "--display-residuals",
            ]
        )


def test_doctor_returns_nonzero_when_missing_deps(monkeypatch, capsys):
    monkeypatch.setattr(
        "formhtr.commands.doctor.check_system_dependencies",
        lambda: [("qpdf", "install hint")],
    )
    code = cli.main(["doctor"])
    out = capsys.readouterr().out
    assert code == 1
    assert "Missing system dependencies" in out
    assert "- qpdf: install hint" in out


def test_automatic_align_writes_json_payload(monkeypatch, capsys):
    payload = {"frontside": {"x": 1}, "backside": None}
    monkeypatch.setattr(
        "formhtr.commands.automatic_align.build_alignment_payload",
        lambda **_kwargs: payload,
    )
    code = cli.main(
        [
            "automatic-align",
            "--pdf-logsheet",
            "scan.pdf",
            "--pdf-template",
            "template.pdf",
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert json.loads(out) == payload
