"""Test version"""

import re

import pytest


@pytest.fixture(scope="module")
def expected_version(yadm):
    """
    Expected semantic version number. This is taken directly out of yadm,
    searching for the VERSION= string.
    """
    with open(yadm, encoding="utf-8") as source_file:
        yadm_version = re.findall(r"VERSION=([^\n]+)", source_file.read())
    if yadm_version:
        return yadm_version[0]
    pytest.fail(f"version not found in {yadm}")
    return "not found"


def test_semantic_version(expected_version):
    """Version is semantic"""
    # semantic version conforms to MAJOR.MINOR.PATCH
    assert re.search(r"^\d+\.\d+\.\d+$", expected_version), "does not conform to MAJOR.MINOR.PATCH"


@pytest.mark.parametrize("cmd", ["--version", "version"])
def test_reported_version(runner, yadm_cmd, cmd, expected_version):
    """Report correct version and bash/git versions"""
    run = runner(command=yadm_cmd(cmd))
    assert run.success
    assert run.err == ""
    assert "bash version" in run.out
    assert "git version" in run.out
    assert run.out.endswith(f"\nyadm version {expected_version}\n")
