"""Test config"""

import os

import pytest

TEST_SECTION = "test"
TEST_ATTRIBUTE = "attribute"
TEST_KEY = f"{TEST_SECTION}.{TEST_ATTRIBUTE}"
TEST_VALUE = "testvalue"
TEST_FILE = f"[{TEST_SECTION}]\n\t{TEST_ATTRIBUTE} = {TEST_VALUE}"


def test_config_no_params(runner, yadm_cmd, supported_configs):
    """No parameters

    Display instructions
    Display supported configs
    Exit with 0
    """

    run = runner(yadm_cmd("config"))

    assert run.success
    assert run.err == ""
    assert "Please read the CONFIGURATION section" in run.out
    for config in supported_configs:
        assert config in run.out


def test_config_read_missing(runner, yadm_cmd):
    """Read missing attribute

    Display an empty value
    Exit with 0
    """

    run = runner(yadm_cmd("config", TEST_KEY))

    assert run.success
    assert run.err == ""
    assert run.out == ""


def test_config_write(runner, yadm_cmd, paths):
    """Write attribute

    Display no output
    Update configuration file
    Exit with 0
    """

    run = runner(yadm_cmd("config", TEST_KEY, TEST_VALUE))

    assert run.success
    assert run.err == ""
    assert run.out == ""
    assert paths.config.read().strip() == TEST_FILE


def test_config_read(runner, yadm_cmd, paths):
    """Read attribute

    Display value
    Exit with 0
    """

    paths.config.write(TEST_FILE)
    run = runner(yadm_cmd("config", TEST_KEY))

    assert run.success
    assert run.err == ""
    assert run.out.strip() == TEST_VALUE


def test_config_update(runner, yadm_cmd, paths):
    """Update attribute

    Display no output
    Update configuration file
    Exit with 0
    """

    paths.config.write(TEST_FILE)

    run = runner(yadm_cmd("config", TEST_KEY, TEST_VALUE + "extra"))

    assert run.success
    assert run.err == ""
    assert run.out == ""

    assert paths.config.read().strip() == TEST_FILE + "extra"


@pytest.mark.usefixtures("ds1_repo_copy")
def test_config_local_read(runner, yadm_cmd, paths, supported_local_configs):
    """Read local attribute

    Display value from the repo config
    Exit with 0
    """

    # populate test values
    for config in supported_local_configs:
        os.system(f'GIT_DIR="{paths.repo}" ' f'git config --local "{config}" "value_of_{config}"')

    # run yadm config
    for config in supported_local_configs:
        run = runner(yadm_cmd("config", config))
        assert run.success
        assert run.err == ""
        assert run.out.strip() == f"value_of_{config}"


@pytest.mark.usefixtures("ds1_repo_copy")
def test_config_local_write(runner, yadm_cmd, paths, supported_local_configs):
    """Write local attribute

    Display no output
    Write value to the repo config
    Exit with 0
    """

    # run yadm config
    for config in supported_local_configs:
        run = runner(yadm_cmd("config", config, f"value_of_{config}"))
        assert run.success
        assert run.err == ""
        assert run.out == ""

    # verify test values
    for config in supported_local_configs:
        run = runner(command=("git", "config", config), env={"GIT_DIR": paths.repo})
        assert run.success
        assert run.err == ""
        assert run.out.strip() == f"value_of_{config}"


def test_config_without_parent_directory(runner, yadm_cmd, paths):
    """Write/read attribute to/from config file with non-existent parent dir

    Update configuration file
    Display value
    Exit with 0
    """

    config_file = paths.root + "/folder/does/not/exist/config"

    run = runner(yadm_cmd("--yadm-config", config_file, "config", TEST_KEY, TEST_VALUE))

    assert run.success
    assert run.err == ""
    assert run.out == ""

    run = runner(yadm_cmd("--yadm-config", config_file, "config", TEST_KEY))

    assert run.success
    assert run.err == ""
    assert run.out.strip() == TEST_VALUE
