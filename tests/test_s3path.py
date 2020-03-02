import pytest

from s3path import S3Path

target_pathes = [
    "s3://test/nadeko.pkl",
    "s3://test/nadeko.msg",
    "s3://test/nadeko2.pkl",
    "s3://test/nadeko2.msg",
    "s3://test/nadeko2.tar.gz",
]


@pytest.mark.parametrize("path,result", zip(target_pathes, ["nadeko.pkl", "nadeko.msg", "nadeko2.pkl", "nadeko2.msg", "nadeko2.tar.gz"]))
def test_name(path, result):
    assert S3Path(path).name == result


@pytest.mark.parametrize("path,result", zip(target_pathes, [".pkl", ".msg", ".pkl", ".msg", ".gz"]))
def test_suffix(path, result):
    assert S3Path(path).suffix == result


@pytest.mark.parametrize("path", target_pathes)
def test_to_str(path):
    assert str(S3Path(path)) == path


@pytest.mark.parametrize("path,result", zip(target_pathes, [".pkl", ".msg", ".pkl", ".msg", ".gz"]))
def test_suffix(path, result):
    assert S3Path(path).suffix == result
