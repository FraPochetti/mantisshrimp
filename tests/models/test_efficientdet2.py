import pytest
from mantisshrimp.imports import *
from mantisshrimp.core import *
from mantisshrimp.models import efficient_det


@pytest.fixture()
def img():
    return 255 * np.ones((4, 4, 3), dtype=np.uint8)


@pytest.fixture()
def labels():
    return [1, 2]


@pytest.fixture()
def bboxes():
    return [BBox.from_xyxy(1, 2, 3, 4), BBox.from_xyxy(4, 3, 2, 1)]


@pytest.fixture()
def records(img, labels, bboxes):
    return [{"img": img, "labels": labels, "bboxes": bboxes}] * 2


def _test_batch(images, targets):
    assert images.shape == (2, 3, 4, 4)
    assert torch.all(images == 1.0)

    assert targets["cls"][0].dtype == torch.float
    assert len(targets["cls"]) == 2
    assert torch.all(targets["cls"][0] == tensor([1, 2], dtype=torch.float))

    assert targets["bbox"][0].dtype == torch.float
    assert len(targets["bbox"]) == 2
    expected_bboxes = tensor([[2, 1, 4, 3], [3, 4, 1, 2]], dtype=torch.float)
    assert torch.all(targets["bbox"][0] == expected_bboxes)


def _test_batch_train(images, targets):
    _test_batch(images=images, targets=targets)
    assert set(targets.keys()) == {"cls", "bbox"}


def _test_batch_valid(images, targets):
    _test_batch(images=images, targets=targets)

    assert set(targets.keys()) == {"cls", "bbox", "img_size", "img_scale"}

    assert targets["img_scale"].dtype == torch.float
    assert torch.all(targets["img_scale"] == tensor([1, 1]))

    assert targets["img_size"].dtype == torch.float
    assert torch.all(targets["img_size"] == tensor([[4, 4], [4, 4]]))


def test_efficient_det_build_train_batch(records):
    images, targets = efficient_det.build_train_batch(records)
    _test_batch_train(images=images, targets=targets)


def test_efficient_det_build_valid_batch(records):
    images, targets = efficient_det.build_valid_batch(records)
    _test_batch_valid(images=images, targets=targets)


def test_efficient_det_train_dataloader(records):
    dl = efficient_det.train_dataloader(records, batch_size=2)
    xb, yb = first(dl)

    _test_batch_train(images=xb, targets=yb)


def test_efficient_det_valid_dataloader(records):
    dl = efficient_det.valid_dataloader(records, batch_size=2)
    xb, yb = first(dl)

    _test_batch_valid(images=xb, targets=yb)